import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..support import audit_log
from ..support.db_auth import resolve_user
from ..support.file_handler import FileHandler
from ..support.globals import log
from ..support.rbac import require_role

router = APIRouter(tags=["Delete Methods"])


@router.delete("/admin/user-data", operation_id="delete_stale_user_data")
def delete_stale_user_data(request: Request, days: Optional[int] = 7, db: Session = Depends(get_db)):
    """Housekeeping: delete every user folder older than `days`; admins only."""
    identity = resolve_user(request, db)
    if identity.user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")
    require_role(identity.user, "admin")

    localpath = FileHandler.get_local_simulation_path()
    if os.path.exists(localpath):
        names = FileHandler.remove_folder_if_older(localpath, days, True)
        if len(names) != 0:
            audit_log.record(
                identity.user.email, "delete_user_data_by_age", ", ".join(names), request, extra={"days": days}
            )
            log.info("Data of %s has been deleted", ", ".join(names))
            return "Data of " + ", ".join(names) + " has been deleted"
    log.info("Nothing has been deleted")
