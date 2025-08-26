# app/utils/file.py

import os
import uuid

from fastapi import HTTPException, UploadFile

from Day5.app.configs import config

IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif"]


async def upload_file(file: UploadFile, upload_dir: str) -> str:

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    # 파일 확장자 분리
    filename, ext = file.filename.rsplit(".", 1) if "." in file.filename else (file.filename, "")

    # UUID가 추가된 유니크한 파일명 생성
    unique_filename = f"{filename}_{uuid.uuid4().hex}.{ext}" if ext else f"{filename}_{uuid.uuid4().hex}"

    upload_dir_path = os.path.join(config.MEDIA_DIR, upload_dir)
    os.makedirs(upload_dir_path, exist_ok=True)  # 업로드 폴더가 없으면 생성

    file_path = f"{upload_dir}/{unique_filename}"

    with open(f"{upload_dir_path}/{unique_filename}", "wb") as f:
        f.write(await file.read())

    return file_path


def delete_file(file_url: str) -> None:
    file_path = f"{config.MEDIA_DIR}/{file_url}"

    if not os.path.exists(file_path):
        return

    os.remove(file_path)


def validate_image_extension(file: UploadFile) -> str:

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    filename, ext = file.filename.rsplit(".", 1) if "." in file.filename else (file.filename, "")
    if ext not in IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"invalid image extension. enable extension: {IMAGE_EXTENSIONS}")
    return ext
