from pathlib import Path

from .dicom import DICOMWriter
from .jpg import JPGWriter
from .nifti import NIfTIWriter
from .png import PNGWriter


class PipelineWriter:
    _writers: dict[str, type] = {
        ".png": PNGWriter,
        ".jpg": JPGWriter,
        ".jpeg": JPGWriter,
        ".nii": NIfTIWriter,
        ".nii.gz": NIfTIWriter,
        ".dcm": DICOMWriter,
    }

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def write(self, image):
        path_str = str(self.path).lower()

        for extension in sorted(self._writers, key=len, reverse=True):
            if path_str.endswith(extension):
                writer_cls = self._writers[extension]
                return writer_cls().write(image, self.path)

        raise ValueError(f"Unsupported image format: {self.path}")
