from abc import ABC, abstractmethod
from pathlib import Path

from medartifact.__core import MedicalImage


class BaseWriter(ABC):

    @abstractmethod
    def write(self, image: MedicalImage, output_path: str | Path):
        raise NotImplementedError
