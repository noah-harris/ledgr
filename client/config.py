import mimetypes
import colorlog
import logging
import os

def make_logger(name: str) -> logging.Logger:
    root = logging.getLogger()
    if not root.handlers:
        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            fmt='%(log_color)s[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt="%H:%M:%S"
        ))
        root.addHandler(handler)
        root.setLevel(logging.DEBUG)
    return logging.getLogger(name)

logger = make_logger('ledgr-client')

IMAGE_DIRECTORY = os.getenv("IMAGE_DIRECTORY").rstrip("/")
SUPPORTED_IMAGE_FORMATS = ["png", "jpg", "jpeg", "gif", "bmp", "pdf"]
FILETYPE_TO_MIMETYPE = {ext: mimetypes.types_map.get(f".{ext}", "application/octet-stream") for ext in SUPPORTED_IMAGE_FORMATS}
FILE_EXPLORER_IMAGE_TYPES = [("Image Files", ";".join([f"*.{ext}" for ext in SUPPORTED_IMAGE_FORMATS]))]
NO_IMAGE_ID = '2740391C-72F7-3986-62E4-1DA7F8D1C57C'
