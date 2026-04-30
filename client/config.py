import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import mimetypes
import os
import requests as _requests

from shared.config import *
from shared.config import make_logger

logger = make_logger('ledgr-client')

FILETYPE_TO_MIMETYPE = {
    ext: mimetypes.types_map.get(f".{ext}", "application/octet-stream")
    for ext in SUPPORTED_IMAGE_FORMATS
}

FILE_EXPLORER_IMAGE_TYPES = [("Image Files", ";".join([f"*.{ext}" for ext in SUPPORTED_IMAGE_FORMATS]))]

NO_IMAGE_ID = '2740391C-72F7-3986-62E4-1DA7F8D1C57C'

def fetch_image_bytes(filename: str) -> bytes | None:
    if not IMAGE_BASE_URL or not filename:
        return None
    try:
        response = _requests.get(f"{IMAGE_BASE_URL}/{filename}", timeout=5)
        response.raise_for_status()
        return response.content
    except Exception:
        return None
