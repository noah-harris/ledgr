import subprocess
import sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

from pathlib import Path
from urllib.parse import unquote
import sqlalchemy
import requests
from html.parser import HTMLParser
import os
import logging
from db import get_connection
from sqlalchemy import exc


logger = logging.getLogger("upload-images")

IMAGE_DIRECTORY = os.getenv("IMAGE_DIRECTORY").rstrip("/")
SUPPORTED_IMAGE_FORMATS = ["png", "jpg", "jpeg", "gif", "bmp", "pdf"]

class _DirectoryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.filenames = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name, val in attrs:
                if name == 'href' and val and not val.startswith('?') and not val.startswith('/'):
                    self.filenames.append(val)

def run():
    logger.debug("Loading Images...")
    resp = requests.get(IMAGE_DIRECTORY, timeout=5)
    resp.raise_for_status()
    parser = _DirectoryParser()
    parser.feed(resp.text)
    for filename in sorted(parser.filenames):
        filename = unquote(filename)
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