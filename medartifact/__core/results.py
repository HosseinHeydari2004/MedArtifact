from dataclasses import dataclass, field
from typing import Any

from .image import MedicalImage


@dataclass
class DetectionResult:
    artifact_type: str  # Types of artifacts such as: noise/ bias_field/ contrast/ motion
    detected: bool  # Has an artifact been detected? True or False
    confidence: float  # Detector Confidence
    score: float | None = None  # The raw algorithm score, if any.
    details: dict[str, Any] = field(default_factory=dict)  # Additional information specific to each Detector


@dataclass
class CorrectionResult:
    artifact_type: str  # Types of artifacts such as: noise/ bias_field/ contrast/ motion
    corrected_image: MedicalImage  # Corrector should return a new/corrected MedicalImage, not just a numpy.ndarray.
    changed: bool  # Has any correction really been made?
    details: dict[str, Any] = field(default_factory=dict)  # Additional correction information


@dataclass
class PipelineResult:
    input_image: MedicalImage  # The image is original.
    final_image: MedicalImage  # The image has been modified.
    detections: list[DetectionResult] = field(default_factory=list)  # A list of all detections
    corrections: list[CorrectionResult] = field(default_factory=list)  # A list of all corrections
    metrics: dict[str, Any] = field(default_factory=dict)  # A list of all metrics

