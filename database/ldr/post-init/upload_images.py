import subprocess
import sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

from pathlib import Path
import sqlalchemy
import requests
import os
import logging
from db import get_connection
from sqlalchemy import exc


logger = logging.getLogger("upload-images")

IMAGE_DIRECTORY = os.getenv("IMAGE_DIRECTORY").rstrip("/")
SUPPORTED_IMAGE_FORMATS = ["png", "jpg", "jpeg", "gif", "bmp", "pdf"]

def run():
    logger.debug("Loading Images...")
    resp = requests.get(IMAGE_DIRECTORY, timeout=5)
    resp.raise_for_status()
    filenames = requests.get(f"{IMAGE_DIRECTORY}/list.json", timeout=5).json()
    print(filenames)
    for filename in filenames:
        filetype = Path(filename).suffix.lower().lstrip(".")
        stem = Path(filename).stem
        if filetype not in SUPPORTED_IMAGE_FORMATS:
            logger.debug(f"Skipping unsupported file: {filename}")
            continue
        with get_connection("ldr") as conn:
            try:
                conn.execute(
                    sqlalchemy.text("INSERT INTO [v_Image] ([FileName], [FileType]) VALUES (:FileName, :FileType)"),
                    parameters={"FileName": stem, "FileType": filetype}
                )
                logger.debug(f"Successfully inserted image: {filename}")
            except Exception as e:
                if "has already been uploaded" in str(e):
                    logger.info(f"Image already exists, skipping: {filename}")
                else:
                    logger.error(f"Error inserting image {filename}: {str(e)}")
          
run()