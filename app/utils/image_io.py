import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Union
from app.core.exceptions import ImageValidationError


def load_image(image_input: Union[str, Path, bytes, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load an image from path, bytes, or numpy array.
    Supports Grayscale (1-channel), BGR (3-channel), and BGRA/RGBA (4-channel).
    
    Returns:
        Tuple[bgr_image, gray_image]
    """
    if isinstance(image_input, np.ndarray):
        img_raw = image_input.copy()
    elif isinstance(image_input, (str, Path)):
        path_str = str(image_input)
        if not Path(path_str).exists():
            raise ImageValidationError(f"Image file does not exist: {path_str}")
        img_raw = cv2.imread(path_str, cv2.IMREAD_UNCHANGED)
        if img_raw is None:
            # Fallback for complex TIFF/PNG formats using PIL
            try:
                from PIL import Image
                pil_img = Image.open(path_str)
                img_raw = np.array(pil_img)
            except Exception as e:
                raise ImageValidationError(f"Failed to decode image file at {path_str}: {str(e)}")
    elif isinstance(image_input, bytes):
        if not image_input or len(image_input) == 0:
            raise ImageValidationError("Uploaded image byte buffer is empty.")
        nparr = np.frombuffer(image_input, np.uint8)
        img_raw = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
        if img_raw is None:
            # Fallback PIL decoding from bytes
            try:
                import io
                from PIL import Image
                pil_img = Image.open(io.BytesIO(image_input))
                img_raw = np.array(pil_img)
            except Exception as e:
                raise ImageValidationError(f"Image cannot be decoded from bytes: {str(e)}")
    else:
        raise ImageValidationError("Unsupported image input type.")

    if img_raw is None or img_raw.size == 0:
        raise ImageValidationError("Image is empty or corrupted.")

    # Channel handling (Grayscale, RGB, BGR, RGBA, BGRA)
    if len(img_raw.shape) == 2:
        gray = img_raw.copy()
        img_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    elif len(img_raw.shape) == 3:
        channels = img_raw.shape[2]
        if channels == 3:
            img_bgr = img_raw.copy()
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        elif channels == 4:
            # Convert RGBA / BGRA to 3-channel BGR
            img_bgr = cv2.cvtColor(img_raw, cv2.COLOR_BGRA2BGR)
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        else:
            raise ImageValidationError(f"Unsupported number of image channels: {channels}")
    else:
        raise ImageValidationError(f"Invalid image array shape: {img_raw.shape}")

    # Validate minimum image dimensions
    h, w = img_bgr.shape[:2]
    if h < 10 or w < 10:
        raise ImageValidationError(f"Image dimensions are too small ({w}x{h} px). Minimum required size is 10x10 px.")

    return img_bgr, gray


def save_image(file_path: Union[str, Path], img: np.ndarray) -> str:
    """Save numpy array as image file (PNG/JPG/TIFF)."""
    path_str = str(file_path)
    Path(path_str).parent.mkdir(parents=True, exist_ok=True)
    
    success = cv2.imwrite(path_str, img)
    if not success:
        # Fallback using PIL
        try:
            from PIL import Image
            if len(img.shape) == 3 and img.shape[2] == 3:
                img_to_save = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                img_to_save = img
            pil_img = Image.fromarray(img_to_save)
            pil_img.save(path_str)
        except Exception as e:
            raise RuntimeError(f"Failed to save image to {path_str}: {str(e)}")
            
    return path_str
