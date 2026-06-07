from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
import os
import shutil
import uuid

from auth.oauth2 import get_current_user
from model.inference import extract_invoice

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/extract-invoice")
async def extract_invoice_api(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = extract_invoice(file_path)

    return JSONResponse(content={
        "user": current_user["email"],
        "result": result
    })