# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Seat enforcement (enterprise plans only).

Call `enforce_seat_limit(db, org)` before creating a new active User row
for that org - local signup or first OAuth login, all
go through this. Community plans have no seat cap (single-tenant,
unlimited local accounts by design); trial has no persistent accounts at
all, so it never reaches this check.

`Organization.licensed_seats` is a cache of LicenseStatus.seats, refreshed
here on every check against license_client.get_status() (which itself
caches - see that module - so this doesn't add a network call per signup).
Keeping the cache on the org row means a seat check never blocks on a
license-server outage beyond what license_client already tolerates.
"""

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db.models import Organization, User
from .license_client import get_status


def _active_seat_count(db: Session, org_id: str) -> int:
    return db.scalar(select(func.count()).select_from(User).where(User.org_id == org_id, User.is_active.is_(True))) or 0


def enforce_seat_limit(db: Session, org: Organization) -> None:
    """No-op for community/trial orgs (no seat cap). For enterprise orgs,
    raises 402 if adding one more active user would exceed the licensed
    seat count."""
    if org.plan != "enterprise":
        return

    status_ = get_status()
    seats = status_.seats
    if org.licensed_seats != seats:
        org.licensed_seats = seats
        db.commit()

    if seats is None:
        return  # license grants enterprise but doesn't cap seats - unlimited

    current = _active_seat_count(db, org.id)
    if current >= seats:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=(
                f"This organization has reached its licensed seat limit ({seats}). "
                "Deactivate an existing user or upgrade your license to add more."
            ),
        )
