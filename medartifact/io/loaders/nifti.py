from pathlib import Path
import nibabel as nib
from medartifact.__core.image import MedicalImage
from .base import BaseLoader
from medartifact.__exceptions.errro import ImageLoadError
from numpy import asarray


class NIfTILoader(BaseLoader):

    def load(self, path: Path | str) -> MedicalImage:
        path = Path(path)

        try:
            nii = nib.load(path)
            data = asarray(nii.dataobj)
        except FileNotFoundError:
            raise ImageLoadError(
                f"NIfTI file not found: {path}"
            )
        except Exception as ex:
            raise ImageLoadError(
                f"Failed to load NIfTI image: {path}"
            ) from ex

        return MedicalImage(
            data=data,
            affine=nii.affine,
            header=nii.header,
            path=path,
            format="nifti"
        )
