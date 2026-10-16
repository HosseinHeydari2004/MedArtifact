from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from numpy import ndarray


@dataclass
class MedicalImage:
    data: ndarray  # image / volume
    affine: ndarray | None = None  # Spatial information in NIfTI
    header: Any | None = None  # Main header format
    metadata: dict[str, Any] = field(default_factory=dict)  # Additional information
    path: Path| str | None = None  # Original file path
    format: str | None = None  # png / jpg / nifti / dicom


