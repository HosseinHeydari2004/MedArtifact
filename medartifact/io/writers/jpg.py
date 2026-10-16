from pathlib import Path

import numpy as np
from PIL import Image

from medartifact.__core import MedicalImage
from medartifact.__exceptions.errro import ImageWriteError
from .base import BaseWriter


class JPGWriter(BaseWriter):

    def write(self, image: MedicalImage, output_path: str | Path) -> Path:
        output_path = Path(output_path)

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            data = np.asarray(image.data)
            pil_image = Image.fromarray(data)
            if pil_image.mode not in ("RGB", "L"):
                pil_image = pil_image.convert("RGB")
            pil_image.save(output_path, format="JPEG", quality=95)
        except Exception as ex:
            raise ImageWriteError(
                f"Failed to write JPG image: {output_path}"
            ) from ex
        return output_path
