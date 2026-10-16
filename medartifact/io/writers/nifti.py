from pathlib import Path

import nibabel as nib
import numpy as np

from medartifact.__core import MedicalImage
from medartifact.__exceptions.errro import ImageWriteError
from .base import BaseWriter


class NIfTIWriter(BaseWriter):

    def write(self, image: MedicalImage, output_path: str | Path) -> Path:
        output_path = Path(output_path)

        try:
            output_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )
            affine = (
                image.affine
                if image.affine is not None
                else np.eye(4)
            )
            nii = nib.Nifti1Image(
                image.data,
                affine,
                header=image.header
            )
            nib.save(nii, output_path)
        except Exception as ex:
            raise ImageWriteError(
                f"Failed to write NIfTI image: {output_path}"
            ) from ex
        return output_path
