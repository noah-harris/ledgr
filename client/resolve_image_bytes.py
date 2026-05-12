from pathlib import Path
import requests

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
            print(f"Error fetching image from URL {image_str}: {e}")
    else:
        try:
            return Path(image_str).read_bytes()
        except Exception as e:
            print(f"Error reading image from file {image_str}: {e}")
