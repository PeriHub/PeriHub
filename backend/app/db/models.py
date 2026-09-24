# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Phase 0 ORM models: organizations, users, oauth identities, admin settings.

model_configs/materials tables are Phase 1 (they depend on users/orgs
existing first) - deliberately not added here yet.

Design notes:
- `User.auth_provider` distinguishes local/oauth/trial rather than having
  separate tables per login method; `OAuthIdentity` only exists for the
  oauth case, where a user may (later) link more than one external
  identity (Keycloak, Google, Azure AD, ...) to a single account.
- `Organization.plan` mirrors LicenseStatus.plan (community/enterprise) but
  is stored on the org row so seat/feature checks don't need a live license
  server call on every request - see support/entitlements.py, which is the
  next thing to wire this into.
- `AdminSettings` is a simple key/value + JSONB value store, scoped by
  optional org_id (NULL = instance-wide default). Deliberately schemaless so
  new settings (branding, SMTP, quotas...) don't need a migration each time.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


def _uuid_str() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Organization(Base):
    """A tenant. Community deployments get exactly one implicit org; every
    row still gets an org_id so the schema doesn't need to change to go
    multi-tenant later."""

    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # "trial" | "community" | "enterprise" - mirrors LicenseStatus.plan.
    plan: Mapped[str] = mapped_column(String(32), nullable=False, default="community")
    # Last-fetched LicenseStatus.seats, cached here so a seat check doesn't
    # need a synchronous license-server round trip - refreshed alongside
    # the normal license_client cache cycle (Phase 1 wiring).
    licensed_seats: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    users: Mapped[list["User"]] = relationship(back_populates="organization")

    def __repr__(self) -> str:
        return f"<Organization {self.name} plan={self.plan}>"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    org_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)

    # Nullable: trial users have neither: they're identified only by `id`.
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    display_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # "local" | "oauth" | "trial"
    auth_provider: Mapped[str] = mapped_column(String(32), nullable=False, default="local")

    # "admin" | "member" | "viewer" - see Phase 1 RBAC.
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="member")

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped["Organization | None"] = relationship(back_populates="users")
    oauth_identities: Mapped[list["OAuthIdentity"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.display_name} ({self.auth_provider})>"


class OAuthIdentity(Base):
    """Links an external OAuth2/OIDC identity to a User.

    Kept separate from User (rather than storing provider fields directly
    on it) so a single account can later link more than one external
    provider without a schema change.
    """

    __tablename__ = "oauth_identities"
    __table_args__ = (UniqueConstraint("provider", "provider_subject", name="uq_oauth_provider_subject"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)

    # "oauth" today; kept as its own column (rather than hardcoded) so a
    # future need to distinguish upstream IdPs (Keycloak, Google, Azure
    # AD, ...) doesn't require a schema change.
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    # `sub` claim / preferred_username from the external token.
    provider_subject: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="oauth_identities")

    def __repr__(self) -> str:
        return f"<OAuthIdentity {self.provider}:{self.provider_subject}>"


class AdminSetting(Base):
    """Runtime-editable admin settings (e.g. external_perilab_url), keyed by
    name and optionally scoped to an org. NULL org_id = instance-wide
    default; an org-scoped row overrides it. See support/admin_settings.py
    for the read/write helper that falls back to env vars when no row
    exists yet, so existing env-var-only deployments keep working."""

    __tablename__ = "admin_settings"
    __table_args__ = (UniqueConstraint("key", "org_id", name="uq_admin_settings_key_org"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    org_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    def __repr__(self) -> str:
        return f"<AdminSetting {self.key}={self.value!r} org={self.org_id}>"


# "private" (owner only) | "team" (members of owner's team) | "org" (anyone
# in owner's org) | "public" (anyone, including trial users - used sparingly,
# e.g. a curated shared material library) - shared by both ModelConfig and
# Material below.
VISIBILITY_PRIVATE = "private"
VISIBILITY_TEAM = "team"
VISIBILITY_ORG = "org"
VISIBILITY_PUBLIC = "public"


class Team(Base):
    """A sub-group within an org (Phase 2). Not every enterprise customer is
    flat - a team gives model configs/materials a visibility scope narrower
    than the whole org without needing a full per-resource ACL table."""

    __tablename__ = "teams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    def __repr__(self) -> str:
        return f"<Team {self.name}>"


class TeamMembership(Base):
    __tablename__ = "team_memberships"
    __table_args__ = (UniqueConstraint("team_id", "user_id", name="uq_team_memberships_team_user"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    team_id: Mapped[str] = mapped_column(ForeignKey("teams.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class Project(Base):
    """A workspace grouping model configs, materials, and (later) results
    under one roof with its own member list (Phase 2). Membership is
    separate from org/team membership - a project can pull members across
    teams for a specific piece of work."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    def __repr__(self) -> str:
        return f"<Project {self.name}>"


class ProjectMembership(Base):
    __tablename__ = "project_memberships"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_project_memberships_project_user"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    # "owner" (can manage members, delete project) | "member" (can add/edit
    # items in the project).
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="member")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


# Queue states for JobQueueEntry.status. "queued" -> "running" -> "done" is
# the normal path; a job can also be "cancelled" (by its owner or an admin)
# or "failed" (backend raised on submit). See support/job_queue.py.
JOB_QUEUED = "queued"
JOB_RUNNING = "running"
JOB_DONE = "done"
JOB_CANCELLED = "cancelled"
JOB_FAILED = "failed"


class JobQueueEntry(Base):
    """Tracks a submitted local (non-cluster) job for fair-share scheduling
    and queue visibility (Phase 3).

    This sits *on top of* the existing filesystem/pid.txt-based ground
    truth for "is a job actually running" (support/job_concurrency.py,
    unchanged) rather than replacing it - pid.txt is what the solver
    container itself writes and can't lie about; this table is PeriHub's
    own bookkeeping for ownership, ordering, and per-user quotas, which
    pid.txt has no concept of. If this table and the filesystem ever
    disagree (e.g. after a crash mid-submit), the filesystem wins for "is
    it running" and this table is corrected by the next scheduler tick
    rather than trusted blindly - see job_queue.reconcile().
    """

    __tablename__ = "job_queue_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    org_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"), nullable=True)

    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_folder_name: Mapped[str] = mapped_column(String(255), nullable=False)
    remotepath: Mapped[str] = mapped_column(String(1000), nullable=False)

    status: Mapped[str] = mapped_column(String(16), nullable=False, default=JOB_QUEUED)
    # "priority" (enterprise, "cluster_priority" feature) | "standard".
    priority: Mapped[str] = mapped_column(String(16), nullable=False, default="standard")
    node_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # The PeriLab API's own job id(s) (support/perilab_api_client.py),
    # set once support/solver_backend.py's submit() actually starts the
    # job - None while still queued. A comma-separated list when one
    # PeriHub submission fans out into several PeriLab jobs (see
    # PeriLabSolverBackend.submit's job_ids handling). This is what
    # status/log/cancel calls use to talk to the PeriLab API - there is no
    # more pid.txt/filesystem fallback for local (non-cluster) jobs.
    perilab_job_id: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Solver options captured at submit time (support/writer/sbatch_writer.py
    # used to bake these into the runPerilab.sh script that was written to
    # disk *before* enqueueing, so a later dequeue just executed it without
    # needing them again - now that submission goes through the PeriLab API
    # instead of a pre-written script, try_run_next() needs them at dequeue
    # time, which can be well after the original request).
    solver_args: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    num_procs: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # "-1" for a single submission, or comma-separated PeriLab-side variant
    # ids for a batch of "<model>_<id>.yaml" files - see
    # PeriLabSolverBackend.submit.
    job_ids: Mapped[str] = mapped_column(String(255), nullable=False, default="-1")

    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    def __repr__(self) -> str:
        return f"<JobQueueEntry {self.model_name}/{self.model_folder_name} ({self.status})>"


class ModelConfig(Base):
    """A saved/shareable model configuration (geometry + solver settings).

    Sharing is deliberately simple for Phase 1 - a visibility enum plus
    org_id scoping, not a per-user ACL table - matching the roadmap's
    "sharing model configs" requirement without over-building. An ACL table
    (explicit per-user/per-team grants) is a natural Phase 2+ upgrade if
    "org" turns out to be too coarse.
    """

    __tablename__ = "model_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    org_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    team_id: Mapped[str | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"), nullable=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    config: Mapped[dict] = mapped_column(JSON, nullable=False)
    visibility: Mapped[str] = mapped_column(String(16), nullable=False, default=VISIBILITY_PRIVATE)
    # List[str] tags for filtering/search (support/rbac.py, routers/library.py)
    # - schemaless on purpose, matching AdminSetting's rationale: engineers
    # will want ad-hoc tags ("v2", "validated", "client-x") without a
    # migration each time a new one shows up.
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    def __repr__(self) -> str:
        return f"<ModelConfig {self.name} ({self.visibility})>"


class Material(Base):
    """A shareable material definition (properties used by the solver).

    Same visibility/org model as ModelConfig - kept as a separate table
    (rather than folding into model_configs with a `kind` column) since
    materials have their own property schema and are looked up
    independently from model configs (e.g. a material picker widget).
    """

    __tablename__ = "materials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    org_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    team_id: Mapped[str | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"), nullable=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    properties: Mapped[dict] = mapped_column(JSON, nullable=False)
    visibility: Mapped[str] = mapped_column(String(16), nullable=False, default=VISIBILITY_PRIVATE)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)  # e.g. "user" | "PeriHub built-in" | DOI
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    def __repr__(self) -> str:
        return f"<Material {self.name} ({self.visibility})>"
