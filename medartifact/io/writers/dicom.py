from pathlib import Path

import numpy as np
import pydicom

from medartifact.__core import MedicalImage
from medartifact.__exceptions.errro import ImageWriteError
from .base import BaseWriter


class DICOMWriter(BaseWriter):

    def write(self, image: MedicalImage, output_path: str | Path):
        output_path = Path(output_path)
        try:
            output_path.parent.mkdir(
                parents=True, exist_ok=True
            )
            data = np.asarray(image.data)
            # For MVP, create a minimal DICOM dataset.
            ds = pydicom.Dataset()
            ds.Rows = data.shape[0]
            ds.Columns = data.shape[1]
            if data.ndim != 2:
                raise ValueError(
                    "Single DICOM writer expects a 2D image"
                )

            if data.dtype == np.uint8:
                ds.BitsAllocated = 8
                ds.BitsStored = 8
                ds.HighBit = 7
                ds.PixelRepresentation = 0
                ds.SamplesPerPixel = 1
                ds.PhotometricInterpretation = "MONOCHROME2"

            elif data.dtype == np.uint16:
                ds.BitsAllocated = 16
                ds.BitsStored = 16
                ds.HighBit = 15
                ds.PixelRepresentation = 0
                ds.SamplesPerPixel = 1
                ds.PhotometricInterpretation = "MONOCHROME2"

            else:
                raise ValueError(
                    f"Unsupported DICOM dtype: {data.dtype}"
                )

            ds.PixelData = data.tobytes()
            pydicom.dcmwrite(
                output_path,
                ds,
            )

        except Exception as e:
            raise ImageWriteError(
                f"Failed to write DICOM image: {output_path}"
            ) from e

        return output_path
