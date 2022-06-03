import os.path
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image


def save_photo(image_arr: np.ndarray, filename: Optional[str] = None) -> Path:
    image = Image.fromarray(image_arr)
    pictures_path = Path.home() / "Pictures"

    if not filename:
        filename = datetime.now().strftime("stella_%Y%m%d%H%M%S")
        counter = 1

        while os.path.exists(pictures_path / filename):
            filename = f"{filename}_{counter}"
            counter += 1

    if not filename.endswith(".jpg"):
        filename += ".jpg"

    image_path = pictures_path / filename
    image.save(image_path)
    return image_path
