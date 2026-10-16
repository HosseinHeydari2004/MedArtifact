from pathlib import Path

from PIL import Image
from numpy import array

from medartifact.__core.image import MedicalImage
from medartifact.__exceptions.errro import ImageLoadError
from .base import BaseLoader


class PNGLoader(BaseLoader):

    def load(self, path: Path | str) -> MedicalImage:
        path = Path(path)
        try:
            image = Image.open(path)
            data = array(image)
        except FileNotFoundError:
            raise ImageLoadError(
                f"Image file not found: '{path}'"
            )
        except Exception as ex:
            raise ImageLoadError(
                f"Failed to load PNG image: '{path}'"
            ) from ex

        return MedicalImage(
            data=data,
            path=path,
            format="png",
            metadata={
                "mode": image.mode
            }
        )
