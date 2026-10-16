# `MedArtifact.core` — Shared Data Contracts

This document explains the data structures defined in `MedArtifact/core/` and how every other module (`io`, `detectors`, `correctors`, `pipeline`) must use them. **Read this before writing a loader, detector, or corrector.**

The goal of `core/` is to give the whole project one consistent "language" for passing images and results between modules, so any detector/corrector/loader can be swapped in or out without breaking the pipeline.

---

## 1. `MedicalImage` — the single data unit used everywhere

Defined in `MedArtifact/core/image.py`:

```python
@dataclass
class MedicalImage:
    data: ndarray                          # image / volume array
    affine: ndarray | None = None          # spatial info (NIfTI/DICOM only)
    header: Any | None = None              # original format header, if any
    metadata: dict[str, Any] = field(default_factory=dict)
    path: Path | None = None               # original file path
    format: str | None = None              # "png" / "jpg" / "nifti" / "dicom"
```

**Golden rule:** any time an image moves between modules (loader → detector → corrector → writer), it must be wrapped in a `MedicalImage`, never a raw `ndarray`.

### For IO (loaders / writers)
- Every loader (`dicom`, `nifti`, `png`, `jpg`) must return a `MedicalImage`.
- Only fill `affine` and `header` when the format actually supports them (NIfTI/DICOM yes, PNG/JPG no — leave `None`).
- `path` and `format` should always be populated.
- Writers should accept a `MedicalImage` and pull whatever fields they need (`data`, `affine`, `header`) from it — don't ask for raw arrays as a separate argument.

### For correctors
- Input to `correct()` is a `MedicalImage`.
- Output must be a **new** `MedicalImage`, not a mutated array.
- Copy `affine`, `header`, and `metadata` from the input unless you have a specific reason to change them.

---

## 2. `DetectionResult` — what every detector returns

Defined in `MedArtifact/core/results.py`:

```python
@dataclass
class DetectionResult:
    artifact_type: str        # "noise" / "bias_field" / "contrast" / "motion"
    detected: bool
    confidence: float
    score: float | None = None
    details: dict[str, Any] = field(default_factory=dict)
```

Each detector (`noise`, `bias_field`, `contrast`, `motion`) returns exactly **one** `DetectionResult`.

- `artifact_type` must match one of the fixed strings above — this is how the pipeline routes results to the right corrector, so don't invent new values without updating `core` first.
- `confidence` is your detector's confidence in the `detected` verdict (0–1).
- `score` is optional — the raw algorithm output (e.g. noise std, gradient magnitude) if it's meaningful outside the detector.
- Put anything algorithm-specific (threshold used, intermediate stats, etc.) into `details`.

Detectors **only report** — they never modify the image.

---

## 3. `CorrectionResult` — what every corrector returns

```python
@dataclass
class CorrectionResult:
    artifact_type: str
    corrected_image: MedicalImage
    changed: bool
    details: dict[str, Any] = field(default_factory=dict)
```

- `corrected_image` must always be a full `MedicalImage`, never a bare array.
- If no correction was actually needed, still return the (unchanged) `MedicalImage` and set `changed=False` — don't return `None`.
- `details` holds correction-specific info (e.g. filter parameters used, iterations run).

---

## 4. `PipelineResult` — the final output of the whole pipeline

```python
@dataclass
class PipelineResult:
    input_image: MedicalImage
    final_image: MedicalImage
    detections: list[DetectionResult] = field(default_factory=list)
    corrections: list[CorrectionResult] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
```

This is only assembled inside `pipeline.py` (the orchestration layer). You generally won't build this yourself unless you're writing an end-to-end test.

---

## 5. Base class contract

Detectors and correctors should implement a shared abstract interface so the pipeline can call any of them interchangeably:

```python
from abc import ABC, abstractmethod
from MedArtifact.__core.image import MedicalImage
from MedArtifact.__core.results import DetectionResult, CorrectionResult


class BaseDetector(ABC):
   @abstractmethod
   def detect(self, image: MedicalImage) -> DetectionResult:
      ...


class BaseCorrector(ABC):
   @abstractmethod
   def correct(self, image: MedicalImage) -> CorrectionResult:
      ...
```

Every concrete detector/corrector should subclass the relevant base class and implement `detect()` / `correct()` with this exact signature.

---

## Ground rules

1. **These dataclasses are frozen contracts.** If you need a new field, propose it first — the rest of the pipeline depends on the current shape.
2. **Always import, never redefine:**
   ```python
   from MedArtifact.__core.image import MedicalImage
   from MedArtifact.__core.results import DetectionResult, CorrectionResult, PipelineResult
   ```
3. **Detectors report, correctors modify.** A detector must never touch `image.data`; a corrector must always return a new `MedicalImage`.
4. **One detector = one `DetectionResult`. One corrector = one `CorrectionResult`.** Don't batch multiple artifact types into a single result object.