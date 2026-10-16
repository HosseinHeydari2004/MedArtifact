from pathlib import Path
import numpy as np
import pydicom as pdm
from medartifact.__core.image import MedicalImage
from .base import BaseLoader
from medartifact.__exceptions.errro import ImageLoadError


class DICOMLoader(BaseLoader):

    def load(self, path: Path | str) -> MedicalImage:
        path = Path(path)

        try:
            ds = pdm.dcmread(path)
            if not hasattr(ds, "PixelData"):
                raise ImageLoadError(
                    f"DICOM file has no pixel data: {path}"
                )
            data = ds.pixel_array
        except FileNotFoundError:
            raise ImageLoadError(
                f"DICOM file not found: {path}"
            )
        except ImageLoadError:
            raise
        except Exception as ex:
            raise ImageLoadError(
                f"Failed to load DICOM image: {path}"
            ) from ex

        metadata = {
            "modality": getattr(ds, "Modality", None),
            "study_instance_uid": getattr(ds, "StudyInstanceUID", None),
            "series_instance_uid": getattr(ds, "SeriesInstanceUID", None),
            "patient_id": getattr(ds, "PatientID", None),
            "rows": getattr(ds, "Rows", None),
            "columns": getattr(ds, "Columns", None),
        }
        return MedicalImage(
            data=np.asarray(data),
            metadata=metadata,
            path=path,
            format="dicom"
        )

