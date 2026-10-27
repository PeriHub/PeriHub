"""Email a user when one of their runs ends (Phase 1, account setting `notify_job_emails`).

Called from sync_status, the one place a run is seen to end in PeriLab - finished, failed, or stopped there (e.g.
cancelled on the PeriLab side). Users cancelling their own run go through cancel_running instead, which doesn't
mail - they know. Only owners can cancel a run and guests have no email, so there is no "stopped by someone else"
path in PeriHub itself. sync_status moves a run out of the active states once, so each run mails at most once.
ponytail: two workers syncing the same run at the same instant could both mail; lock per run if PeriHub ever
runs many workers.
"""

from threading import Thread

from sqlalchemy.orm import Session

from ..db.models import JOB_CANCELLED, JOB_DONE, JOB_FAILED, JobQueueEntry, User
from .globals import log, public_url
from .mailer import send_mail, smtp_configured

_OUTCOME = {JOB_DONE: "finished", JOB_FAILED: "failed", JOB_CANCELLED: "was stopped"}


def _duration(entry: JobQueueEntry) -> str:
    start = entry.started_at or entry.submitted_at
    if not start or not entry.finished_at:
        return "unknown"
    # SQLite hands timestamps back naive; compare like with like.
    seconds = int((entry.finished_at.replace(tzinfo=None) - start.replace(tzinfo=None)).total_seconds())
    minutes, seconds = divmod(max(seconds, 0), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s"


def notify_job_ended(db: Session, entry: JobQueueEntry) -> None:
    """Mails the run's owner if they opted in. Never raises - a run must not fail over its notification."""
    try:
        outcome = _OUTCOME.get(entry.status)
        user = db.get(User, entry.user_id)
        if outcome is None or user is None or not user.notify_job_emails or not user.email or not smtp_configured():
            return
        name = f"{entry.model_name} / {entry.model_folder_name}"
        lines = [
            f"Hello {user.display_name},",
            "",
            f"your PeriHub run {name} {outcome}.",
            "",
            f"Status: {entry.status}",
            f"Run time: {_duration(entry)}",
        ]
        if entry.error:
            lines.append(f"Error: {entry.error}")
        if public_url:
            lines += ["", f"Open PeriHub: {public_url}/perihub"]
        lines += ["", "You get these emails because they're switched on in your PeriHub account settings."]
        # Off the request thread: sync_status also runs inside status polls, which shouldn't wait on SMTP.
        Thread(
            target=send_mail, args=(user.email, f"PeriHub: {name} {outcome}", "\n".join(lines) + "\n"), daemon=True
        ).start()
    except Exception as exc:  # noqa: BLE001 - see docstring
        log.warning("job_notifications: could not notify about run %s: %s", entry.id, exc)
