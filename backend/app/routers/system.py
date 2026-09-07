import os
import subprocess

from fastapi import APIRouter, Depends, HTTPException, status

from app.models import User
from app.services.auth import current_user

router = APIRouter(prefix="/api/system", tags=["system"])
UPDATE_SCRIPT = "/var/www/html/vr/update_key3in.sh"


@router.post("/update", status_code=status.HTTP_202_ACCEPTED)
async def update_application(_: User = Depends(current_user)):
    if not os.path.isfile(UPDATE_SCRIPT) or not os.access(UPDATE_SCRIPT, os.X_OK):
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Сценарий обновления недоступен")
    try:
        subprocess.Popen(
            [UPDATE_SCRIPT],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError as error:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Не удалось запустить обновление") from error
    return {"status": "started"}
