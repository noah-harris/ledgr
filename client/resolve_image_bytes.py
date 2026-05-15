from pathlib import Path
import requests
from config import make_logger

logger = make_logger(__name__)

def resolve_image_bytes(image: str | Path | bytes | None) -> bytes | None:

    if isinstance(image, bytes):
        return image

    if image is None:
        return None

    image_str = str(image)

    if image_str.lower().startswith(("http:", "https:")):
        try:
            response = requests.get(image_str, timeout=5)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Error fetching image from URL {image_str}: {e}")
    else:
        try:
            return Path(image_str).read_bytes()
        except Exception as e:
            logger.error(f"Error reading image from file {image_str}: {e}")
