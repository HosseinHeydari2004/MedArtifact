from pathlib import Path

from .dicom import DICOMLoader
from .jpg import JPGLoader
from .nifti import NIfTILoader
from .png import PNGLoader


class PipelineLoader:
    _loaders: dict[str, type] = {
        ".png": PNGLoader,
        ".jpg": JPGLoader,
        ".jpeg": JPGLoader,
        ".nii": NIfTILoader,
        ".nii.gz": NIfTILoader,
        ".dcm": DICOMLoader,
    }

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self):
        path_str = str(self.path).lower()

        for extension in sorted(self._loaders, key=len, reverse=True):
            if path_str.endswith(extension):
                loader_cls = self._loaders[extension]
                return loader_cls().load(self.path)

        raise ValueError(f"Unsupported image format: {self.path}")
