from abc import abstractmethod, ABC
from pathlib import Path

from medartifact.__core.image import MedicalImage


class BaseLoader(ABC):
    """A base class for a common contract for all loaders"""

    def __init__(self, path: Path | str = None) -> None:
        self.path = path

    @abstractmethod
    def load(self, path: Path | str) -> MedicalImage:
        """A base method for a common contract for all loader methods"""
        raise NotImplementedError
