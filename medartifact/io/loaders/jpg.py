from pathlib import Path

import numpy as np
from PIL import Image

from medartifact.__core.image import MedicalImage
from medartifact.__exceptions.errro import ImageLoadError
from medartifact.io.loaders.base import BaseLoader


class JPGLoader(BaseLoader):

    def load(self, path: str | Path) -> MedicalImage:

        path = Path(path)

        try:
            image = Image.open(path)

            data = np.array(image)

        except FileNotFoundError:
            raise ImageLoadError(
                f"File not found: {path}"
            )

        except Exception as e:
            raise ImageLoadError(
                f"Failed to load JPG image: {path}"
            ) from e

        return MedicalImage(
            data=data,
            path=f"'{path}'",
            format="jpg",
            metadata={
                "mode": image.mode
            }
        )



