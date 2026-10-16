# 🏥 MedArtifact

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![GitHub Stars](https://img.shields.io/github/stars/HosseinHeydari2004/medvision?style=flat&logo=github)](https://github.com/HosseinHeydari2004/medvision/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/HosseinHeydari2004/medvision?style=flat&logo=github)](https://github.com/HosseinHeydari2004/medvision/issues)
[![Last Commit](https://img.shields.io/github/last-commit/HosseinHeydari2004/medvision?style=flat&logo=git)](https://github.com/HosseinHeydari2004/medvision/commits/main)
[![Repo Size](https://img.shields.io/github/repo-size/HosseinHeydari2004/medvision?style=flat&logo=github)](https://github.com/HosseinHeydari2004/medvision)
[![Medical Imaging](https://img.shields.io/badge/Domain-Medical%20Imaging-red)](#)
[![DICOM](https://img.shields.io/badge/Format-DICOM-orange)](#)
[![NIfTI](https://img.shields.io/badge/Format-NIfTI-blue)](#)
[![MONAI](https://img.shields.io/badge/Medical%20AI-MONAI-4B5563)](https://monai.io/)

### Medical Image Quality & Artifact Processing Library

**Detect. Understand. Correct. Before Your Model Sees the Image.**

`MedArtifact` is a modular Python library for **detecting and correcting common medical image artifacts before they affect downstream AI and computer vision models**.

It provides a structured preprocessing layer for medical imaging pipelines, targeting artifacts such as:

- 🟡 Noise
- 🟠 Bias field / intensity inhomogeneity
- 🔵 Poor contrast
- 🔴 Motion artifacts

Instead of relying on scattered preprocessing scripts, `medvision` turns artifact handling into a **reproducible, measurable, and extensible engineering stage**.

---

## 🎯 Why medvision?

Medical imaging data is rarely perfect.

Scanner noise, intensity inhomogeneity, inconsistent contrast, and patient motion can affect image quality and potentially influence downstream model performance.

A common approach is to build ad-hoc preprocessing scripts around individual projects:

```text
Medical Image
     ↓
  Custom Script
     ↓
  More Scripts
     ↓
  ML Model
     ↓
Unexpected Results
```

This quickly becomes difficult to maintain, reproduce, test, and extend.

`medvision` treats image-quality processing as a **first-class engineering layer**:

```text
Medical Image
      │
      ▼
    Load
      │
      ▼
   Detect
      │
      ▼
  Diagnose
      │
      ▼
   Correct
      │
      ▼
   Validate
      │
      ▼
    Write
      │
      ▼
Downstream AI Model
```

> **The goal is simple: make medical image preprocessing explicit, measurable, reusable, and reproducible.**

---

## ✨ Core Features

### 🔍 Artifact Detection

Each artifact type has a dedicated detector responsible for identifying whether the artifact is present.

A detector can report:

- Whether an artifact was detected
- Detection confidence
- Raw detection score
- Additional diagnostic information when available

**Detectors report — they never modify the image.**

---

### 🛠️ Artifact Correction

When an artifact is detected, the corresponding corrector can process the image.

Correctors:

- Receive a `MedicalImage`
- Apply a specific correction algorithm
- Return a new `MedicalImage`
- Report whether a correction was actually applied

The original image is not silently mutated.

---

### 📦 Format-Agnostic I/O

Different file formats should not force the rest of the pipeline to behave differently.

`medvision` normalizes supported formats into a common internal representation:

| Format | Support |
|---|---:|
| PNG | ✅ |
| JPG / JPEG | ✅ |
| NIfTI | ✅ |
| DICOM | ✅ |

```text
PNG ─────┐
JPG ─────┤
NIfTI ───┼──▶ MedicalImage ──▶ Processing ──▶ Output
DICOM ───┘
```

Spatial metadata such as affine information and format-specific headers can be preserved where applicable.

---

### 🔄 Batch Processing

Process individual images or entire directories through the same I/O layer.

```python
from medvision.io import IOPipeline

pipeline = IOPipeline()

images, report = pipeline.load("data/raw/")

print(report.summary())

for err in report.errors:
    print("LOAD FAIL:", err.path, err.error_type, err.error)
```

Batch writing supports both a default output format and automatic format preservation.

```python
written, report = pipeline.write_batch(
    images,
    output_dir="data/processed/",
    filename_pattern="scan_{index:04d}{ext}",
    extension_mode="default",
    default_extension=".nii.gz",
)

print(report.summary())
```

Or preserve each image's original format:

```python
written_auto, report_auto = pipeline.write_batch(
    images,
    output_dir="data/processed_auto/",
    filename_pattern="scan_{index:04d}{ext}",
    extension_mode="auto",
)

print(report_auto.summary())
```

---

## 🧠 Architecture

`medvision` is built around a small set of explicit data contracts.

```text
┌──────────────┐
│    Loader    │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│   MedicalImage   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│     Detector     │
│                  │
│  noise           │
│  bias field      │
│  contrast        │
│  motion          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ DetectionResult  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    Corrector     │
│                  │
│  noise           │
│  bias field      │
│  contrast        │
│  motion          │
└────────┬─────────┘
         │
         ▼
┌───────────────────┐
│ CorrectionResult  │
└─────────┬─────────┘
          │
          ▼
┌──────────────────┐
│      Writer      │
└──────────────────┘
```

### `MedicalImage`

The central data object used throughout the library.

It represents:

- Image pixel / voxel data
- Source format
- Spatial metadata
- Affine information when available
- Format-specific metadata such as headers

No module needs to pass around a bare NumPy array.

---

### `DetectionResult`

Represents the output of an artifact detector.

It answers questions such as:

```text
Was an artifact detected?
How confident are we?
What was the raw detection score?
```

A detector reports findings without modifying the input image.

---

### `CorrectionResult`

Represents the result of an artifact correction.

It contains:

- The resulting `MedicalImage`
- Whether a correction was applied
- Correction-related information

Correctors return a new image instead of silently mutating their input.

---

### `PipelineResult`

Connects the complete processing lifecycle.

Conceptually:

```text
Original Image
      │
      ├── Detection Results
      │
      ├── Correction Results
      │
      ▼
Final Image
```

This makes the processing history explicit and inspectable.

---

## 🏗️ Project Structure

```text
medvision/
│
├── core/
│   ├── medical_image.py
│   ├── detection_result.py
│   ├── correction_result.py
│   └── pipeline_result.py
│
├── io/
│   ├── loaders/
│   │   ├── png.py
│   │   ├── jpg.py
│   │   ├── nifti.py
│   │   └── dicom.py
│   │
│   └── writers/
│       ├── png.py
│       ├── jpg.py
│       ├── nifti.py
│       └── dicom.py
│
├── detectors/
│   ├── base.py
│   ├── noise.py
│   ├── bias_field.py
│   ├── contrast.py
│   └── motion.py
│
├── correctors/
│   ├── base.py
│   ├── noise.py
│   ├── bias_field.py
│   ├── contrast.py
│   └── motion.py
│
├── utils/
│   ├── metrics.py
│   └── visualization.py
│
├── exceptions/
│   └── ...
│
└── pipeline.py
```

The exact implementation may evolve, but the architectural boundary remains:

```text
I/O → Core Contracts → Detection → Correction → I/O
```

---

## 🔌 Extensible by Design

Adding a new artifact should not require rewriting the pipeline.

Detectors follow a common interface:

```python
class BaseDetector:
    def detect(self, image):
        ...
```

Correctors follow a common interface:

```python
class BaseCorrector:
    def correct(self, image):
        ...
```

This allows the orchestration layer to work with different algorithms through stable interfaces.

For example:

```text
BaseDetector
     │
     ├── NoiseDetector
     ├── BiasFieldDetector
     ├── ContrastDetector
     └── MotionDetector
```

and:

```text
BaseCorrector
     │
     ├── NoiseCorrector
     ├── BiasFieldCorrector
     ├── ContrastCorrector
     └── MotionCorrector
```

A new artifact can therefore be introduced without coupling it to the rest of the system.

---

# 🚀 Usage

### Load Images

```python
from medvision.io import IOPipeline

pipeline = IOPipeline()

images, load_report = pipeline.load("data/raw/")

print(load_report.summary())

for err in load_report.errors:
    print("LOAD FAIL:", err.path, err.error_type, err.error)
```

### Write All Images as NIfTI

```python
written, write_report = pipeline.write_batch(
    images,
    output_dir="data/processed/",
    filename_pattern="scan_{index:04d}{ext}",
    extension_mode="default",
    default_extension=".nii.gz",
)

print(write_report.summary())
```

### Preserve the Original Format

```python
written_auto, report_auto = pipeline.write_batch(
    images,
    output_dir="data/processed_auto/",
    filename_pattern="scan_{index:04d}{ext}",
    extension_mode="auto",
)

print(report_auto.summary())
```

### Verify an Output

```python
check, check_report = pipeline.load(written[0])

print(check_report.summary())
```

---

## 🔬 Intended Workflow

The long-term workflow is designed around a simple principle:

> **Do not correct an artifact just because a correction algorithm exists. Detect it first.**

A typical pipeline can therefore look like:

```text
             ┌───────────────┐
             │ Medical Image │
             └───────┬───────┘
                     │
                     ▼
              ┌────────────┐
              │   Detect   │
              └─────┬──────┘
                    │
          ┌─────────┴─────────┐
          │                   │
       No Artifact         Detected
          │                   │
          │                   ▼
          │             ┌───────────┐
          │             │  Correct  │
          │             └─────┬─────┘
          │                   │
          └─────────┬─────────┘
                    ▼
              ┌───────────┐
              │  Validate │
              └─────┬─────┘
                    │
                    ▼
              ┌───────────┐
              │   Write   │
              └─────┬─────┘
                    │
                    ▼
              Clean Dataset
                    │
                    ▼
              AI / ML Model
```

This separation makes it possible to evaluate each stage independently.

---

## 🧪 Design Principles

`medvision` is built around several engineering principles:

### 1. Detection before correction

No correction should be applied blindly.

### 2. Explicit data contracts

Every major stage communicates through defined objects rather than loosely structured dictionaries or raw arrays.

### 3. No hidden mutation

Processing should be predictable and reproducible.

### 4. Separation of concerns

I/O, detection, correction, orchestration, and utilities remain separate responsibilities.

### 5. Reproducibility

The same input and processing configuration should produce a traceable result.

### 6. Extensibility

New formats, detectors, and correction algorithms should integrate through stable interfaces.

### 7. Production-oriented engineering

The project is designed with error reporting, batch processing, validation, and maintainability in mind rather than only notebook-based experimentation.

---

## 📊 Current Artifact Roadmap

| Artifact | Detection | Correction | Status |
|---|:---:|:---:|---|
| Noise | 🚧 | 🚧 | In development |
| Bias Field | 🚧 | 🚧 | In development |
| Contrast | 🚧 | 🚧 | In development |
| Motion | 🚧 | 🚧 | In development |

> The repository is under active development. Check the source code for the current implementation status of each component.

---

## 🧰 Tech Stack

- **Python**
- **MONAI** — medical imaging and deep learning ecosystem
- **OpenCV** — image processing
- **NumPy** — numerical computing
- **SciPy** — scientific computing
- **scikit-image** — image processing
- **NiBabel** — NIfTI and neuroimaging formats
- **pydicom** — DICOM
- **Pillow** — PNG/JPG image handling
- **Pydantic** — structured data validation

---

## 📦 Installation

`medvision` is currently developed directly from source and is not yet published as a PyPI package.

```bash
git clone https://github.com/HosseinHeydari2004/medvision.git
cd medvision

pip install -r requirements.txt
```

---

## 🗺️ Roadmap

The project is being developed incrementally around the core architecture.

### I/O

- [x] Unified image representation
- [x] PNG loading
- [x] JPG/JPEG loading
- [x] NIfTI loading
- [x] DICOM loading
- [x] Batch loading
- [x] Batch writing
- [x] Output extension control
- [x] Format-preserving output mode

### Artifact Detection

- [ ] Noise detection
- [ ] Bias-field detection
- [ ] Contrast detection
- [ ] Motion detection

### Artifact Correction

- [ ] Noise correction
- [ ] Bias-field correction
- [ ] Contrast correction
- [ ] Motion correction

### Pipeline

- [ ] End-to-end artifact pipeline
- [ ] Configurable processing stages
- [ ] Structured pipeline reports
- [ ] Processing metrics
- [ ] Visualization utilities

### Quality & Engineering

- [ ] Expanded unit test coverage
- [ ] Integration tests
- [ ] Benchmark datasets
- [ ] Documentation
- [ ] CI/CD
- [ ] Package release

---

## 🤝 Contributing

Contributions are welcome.

Before adding or modifying a loader, detector, corrector, or core contract:

1. Read [`core-architecture.md`](./core-architecture.md).
2. Follow the existing interfaces.
3. Use the relevant base class instead of introducing a parallel interface.
4. Keep responsibilities separated.
5. Add tests for new behavior.
6. Avoid changing core data contracts without first discussing the architectural impact.

The most important contracts are:

```text
MedicalImage
DetectionResult
CorrectionResult
PipelineResult
```

Changes to these objects can affect the entire processing pipeline.

---

## 📚 Architecture Documentation

For a deeper explanation of the architecture, contracts, and implementation rules, see:

**[`core-architecture.md`](./core-architecture.md)**

This document is the starting point for contributors working on the core pipeline.

---

## 👥 Contributors

`medvision` is developed collaboratively by engineers and researchers working across **AI, medical imaging, computer vision, and software engineering**.

| Contributor | Focus |
|---|---|
| **Hossein Heydari** | Architecture · Core Engineering · Medical Imaging Pipeline |
| **Seyede Reyhane Khorashadizade** | Computer Vision · Image Processing · Deep Learning · Healthcare AI |

### 🔗 Contributors

- **Hossein Heydari** — [GitHub](https://github.com/HosseinHeydari2004)
- **Seyede Reyhane Khorashadizade** — [GitHub](https://github.com/Seyede-Reyhane-Khorashadizade)

---

## ⚠️ Project Status

`medvision` is an **actively developed open-source engineering project**.

The core architecture and data contracts provide the foundation of the system, while artifact detectors and correction algorithms are being implemented incrementally.

The current repository should therefore be considered a **work in progress**, not a finished clinical or diagnostic product.

`medvision` is intended as an engineering and research tool for medical image preprocessing. It is **not a medical device and should not be used for clinical diagnosis or treatment decisions without appropriate validation, regulatory review, and clinical oversight.**


---

## 📄 License

A license has not yet been specified for this repository.

Check the repository for the current licensing status before using or redistributing the project.

---

<div align="center">

### 🏥 medvision

**Clean the image before you blame the model.**

Built for reproducible medical imaging pipelines.

</div>
