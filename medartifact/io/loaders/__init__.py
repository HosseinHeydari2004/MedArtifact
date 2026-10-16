from .png import PNGLoader
from .jpg import JPGLoader
from .dicom import DICOMLoader
from .nifti import NIfTILoader
from .pipeline import PipelineLoader

__all__ = [
    "PNGLoader",
    "JPGLoader",
    "DICOMLoader",
    "NIfTILoader",
    "PipelineLoader"
]