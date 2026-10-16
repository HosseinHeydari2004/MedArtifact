"""
medartifact.io.pipeline
=====================

High-level I/O pipeline for medical images.

This module exposes :class:`IOPipeline`, a thin orchestration layer that
selects the appropriate loader/writer based on file extension, and provides
batch operations with progress reporting.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Literal

from tqdm import tqdm

from medartifact.__core import MedicalImage
from medartifact.io import PipelineLoader
from medartifact.io import PipelineWriter

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUPPORTED_EXTENSIONS: set[str] = {
    ".png",
    ".jpg",
    ".jpeg",
    ".nii",
    ".nii.gz",
    ".dcm",
}

ExtensionMode = Literal["auto", "manual", "default"]


# ---------------------------------------------------------------------------
# Report dataclasses
# ---------------------------------------------------------------------------

@dataclass
class IOItemError:
    """
    Represents a single failed I/O operation.

    Attributes
    ----------
    path : Path
        Path that caused the failure.
    error : str
        Human-readable error message.
    error_type : str
        Class name of the raised exception.
    """

    path: Path
    error: str
    error_type: str


@dataclass
class IOResult:
    """
    Structured report returned after load/write operations.

    Attributes
    ----------
    operation : str
        Name of the operation: ``"load"``, ``"load_directory"``,
        ``"write"`` or ``"write_batch"``.
    total : int
        Total number of items processed.
    succeeded : int
        Number of items processed successfully.
    failed : int
        Number of items that failed.
    duration_sec : float
        Wall-clock duration of the operation in seconds.
    outputs : list[Path]
        Paths that were successfully produced or read.
    errors : list[IOItemError]
        List of errors encountered during the operation.
    """

    operation: str
    total: int = 0
    succeeded: int = 0
    failed: int = 0
    duration_sec: float = 0.0
    outputs: list[Path] = field(default_factory=list)
    errors: list[IOItemError] = field(default_factory=list)

    def summary(self) -> str:
        """
        Return a short human-readable summary of the result.

        Returns
        -------
        str
            Summary string, e.g. ``"[write_batch] 8/10 succeeded in 1.23s"``.
        """
        return (
                f"[{self.operation}] "
                f"{self.succeeded}/{self.total} succeeded "
                f"in {self.duration_sec:.2f}s"
                + (f" ({self.failed} failed)" if self.failed else "")
        )


# ---------------------------------------------------------------------------
# IOPipeline
# ---------------------------------------------------------------------------

class IOPipeline:
    """
    Handles image input/output operations with reporting and progress bars.

    Supports
    --------
    - Loading a single image
    - Loading images from a directory (with progress bar)
    - Writing a single image
    - Writing multiple images (batch) to a directory
      with auto/manual/default extension selection (with progress bar)
    """

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load(
            self,
            input_path: str | Path,
            *,
            show_progress: bool = True,
    ) -> tuple[list[MedicalImage], IOResult]:
        """
        Load one image or every supported image inside a directory.

        Parameters
        ----------
        input_path : str | Path
            Path to a file or directory.
        show_progress : bool, default True
            Whether to display a tqdm progress bar when loading a
            directory.

        Returns
        -------
        tuple[list[MedicalImage], IOResult]
            The loaded images and a structured report.

        Raises
        ------
        FileNotFoundError
            If ``input_path`` does not exist.
        ValueError
            If ``input_path`` is neither a file nor a directory.
        """
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(
                f"Input path does not exist: {input_path}"
            )

        start = time.perf_counter()

        if input_path.is_file():
            result = self._load_single(input_path)
        elif input_path.is_dir():
            result = self._load_directory(
                input_path,
                show_progress=show_progress,
            )
        else:
            raise ValueError(f"Invalid input path: {input_path}")

        result.duration_sec = time.perf_counter() - start
        return result.outputs, result  # type: ignore[return-value]

    def _load_single(self, path: Path) -> IOResult:
        """
        Load a single file and wrap the outcome in an :class:`IOResult`.

        Parameters
        ----------
        path : Path
            File to load.

        Returns
        -------
        IOResult
            Report containing the loaded image (inside ``outputs``) or
            the error.
        """
        result = IOResult(operation="load", total=1)

        try:
            image = self._load_file(path)
            result.succeeded = 1
            result.outputs.append(path)
            # Store the loaded image on the result for convenience.
            setattr(result, "images", [image])
        except Exception as e:  # noqa: BLE001
            result.failed = 1
            result.errors.append(
                IOItemError(
                    path=path,
                    error=str(e),
                    error_type=type(e).__name__,
                )
            )

        return result

    def _load_directory(
            self,
            directory: Path,
            *,
            show_progress: bool = True,
    ) -> IOResult:
        """
        Load every supported file under ``directory`` recursively.

        Parameters
        ----------
        directory : Path
            Directory to scan.
        show_progress : bool, default True
            Whether to display a tqdm progress bar.

        Returns
        -------
        IOResult
            Report with loaded images stored on the ``images`` attribute.
        """
        files = sorted(
            path
            for path in directory.rglob("*")
            if path.is_file() and self._is_supported(path)
        )

        result = IOResult(
            operation="load_directory",
            total=len(files),
        )
        images: list[MedicalImage] = []

        iterator: Iterable[Path] = files
        if show_progress:
            iterator = tqdm(
                files,
                desc="Loading",
                unit="file",
            )

        for path in iterator:
            try:
                images.append(self._load_file(path))
                result.succeeded += 1
                result.outputs.append(path)
            except Exception as e:  # noqa: BLE001
                result.failed += 1
                result.errors.append(
                    IOItemError(
                        path=path,
                        error=str(e),
                        error_type=type(e).__name__,
                    )
                )

        setattr(result, "images", images)
        return result

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------

    def write(
            self,
            image: MedicalImage,
            output_path: str | Path,
    ) -> tuple[Path, IOResult]:
        """
        Write a single image to ``output_path``.

        Parameters
        ----------
        image : MedicalImage
            Image to write.
        output_path : str | Path
            Destination file path. The extension determines the writer.

        Returns
        -------
        tuple[Path, IOResult]
            The written path and a structured report.

        Raises
        ------
        Exception
            Any error raised by the underlying writer is re-raised after
            being recorded in the report.
        """
        output_path = Path(output_path)
        self._ensure_parent_dir(output_path)

        result = IOResult(operation="write", total=1)
        start = time.perf_counter()

        try:
            writer = PipelineWriter(path=output_path)
            written = writer.write(image)
            result.succeeded = 1
            result.outputs.append(written)
        except Exception as e:  # noqa: BLE001
            result.failed = 1
            result.errors.append(
                IOItemError(
                    path=output_path,
                    error=str(e),
                    error_type=type(e).__name__,
                )
            )
            result.duration_sec = time.perf_counter() - start
            raise

        result.duration_sec = time.perf_counter() - start
        return written, result

    def write_batch(
            self,
            images: Iterable[MedicalImage],
            output_dir: str | Path,
            *,
            filename_pattern: str = "image_{index}{ext}",
            extension: str | None = None,
            extension_mode: ExtensionMode = "default",
            default_extension: str = ".nii.gz",
            skip_errors: bool = True,
            show_progress: bool = True,
    ) -> tuple[list[Path], IOResult]:
        """
        Write multiple images into a directory.

        Parameters
        ----------
        images : Iterable[MedicalImage]
            Images to write.
        output_dir : str | Path
            Directory where images will be saved.
        filename_pattern : str, default "image_{index}{ext}"
            Pattern for output filenames. Supports:

            - ``{index}`` : zero-based index of the image
            - ``{ext}``   : file extension (with dot, e.g. ``".nii.gz"``)
        extension : str | None, optional
            Explicit extension, only used when ``extension_mode="manual"``.
        extension_mode : {"auto", "manual", "default"}, default "default"
            Strategy used to determine the extension for each file:

            - ``"auto"``    : derived from each image (metadata/path).
                              Falls back to ``default_extension``.
            - ``"manual"``  : ``extension`` is used for all images.
                              Raises ``ValueError`` if ``extension`` is None.
            - ``"default"`` : ``default_extension`` is used for all images.
        default_extension : str, default ".nii.gz"
            Fallback / default extension.
        skip_errors : bool, default True
            If True, failed writes are recorded and the loop continues.
            If False, the first error is raised.
        show_progress : bool, default True
            Whether to display a tqdm progress bar.

        Returns
        -------
        tuple[list[Path], IOResult]
            List of successfully written paths and a structured report.

        Raises
        ------
        ValueError
            If ``extension_mode`` is invalid, or ``extension_mode="manual"``
            without ``extension``.
        Exception
            The first writer error when ``skip_errors=False``.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if extension_mode not in ("auto", "manual", "default"):
            raise ValueError(
                f"Invalid extension_mode: {extension_mode!r}. "
                f"Expected one of: 'auto', 'manual', 'default'."
            )

        default_ext = self._normalize_ext(default_extension)

        manual_ext: str | None = None
        if extension_mode == "manual":
            if extension is None:
                raise ValueError(
                    "extension_mode='manual' requires `extension` to be set."
                )
            manual_ext = self._normalize_ext(extension)

        images_list = list(images)
        result = IOResult(
            operation="write_batch",
            total=len(images_list),
        )
        written_paths: list[Path] = []

        start = time.perf_counter()

        iterator: Iterable[tuple[int, MedicalImage]] = enumerate(images_list)
        if show_progress:
            iterator = tqdm(
                iterator,
                total=len(images_list),
                desc="Writing",
                unit="file",
            )

        for index, image in iterator:
            if extension_mode == "auto":
                ext = self._resolve_auto_extension(image, default_ext)
            elif extension_mode == "manual":
                ext = manual_ext  # type: ignore[assignment]
            else:
                ext = default_ext

            filename = filename_pattern.format(index=index, ext=ext)
            output_path = output_dir / filename

            try:
                writer = PipelineWriter(path=output_path)
                written = writer.write(image)
                written_paths.append(written)
                result.succeeded += 1
                result.outputs.append(written)
            except Exception as e:  # noqa: BLE001
                result.failed += 1
                result.errors.append(
                    IOItemError(
                        path=output_path,
                        error=str(e),
                        error_type=type(e).__name__,
                    )
                )
                if not skip_errors:
                    result.duration_sec = time.perf_counter() - start
                    raise

        result.duration_sec = time.perf_counter() - start
        return written_paths, result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_file(self, path: Path) -> MedicalImage:
        """
        Load a single file using :class:`PipelineLoader`.

        Parameters
        ----------
        path : Path
            File to load.

        Returns
        -------
        MedicalImage
            The loaded image.

        Raises
        ------
        ValueError
            If the file extension is not supported.
        """
        if not self._is_supported(path):
            raise ValueError(f"Unsupported image format: {path}")

        loader = PipelineLoader(path=path)
        return loader.load()

    @staticmethod
    def _ensure_parent_dir(output_path: Path) -> None:
        """
        Create the parent directory of ``output_path`` if it does not exist.

        Parameters
        ----------
        output_path : Path
            Destination path whose parent must exist.
        """
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _is_supported(path: Path) -> bool:
        """
        Return True if the file extension is supported.

        Parameters
        ----------
        path : Path
            Path to check.

        Returns
        -------
        bool
            Whether the extension is supported.
        """
        filename = path.name.lower()
        if filename.endswith(".nii.gz"):
            return True
        return path.suffix.lower() in SUPPORTED_EXTENSIONS

    @staticmethod
    def _normalize_ext(ext: str) -> str:
        """
        Ensure the extension starts with a dot.

        Parameters
        ----------
        ext : str
            Extension, with or without a leading dot.

        Returns
        -------
        str
            Normalized extension starting with ``"."``.

        Raises
        ------
        ValueError
            If ``ext`` is empty.
        """
        if not ext:
            raise ValueError("Extension cannot be empty.")
        return ext if ext.startswith(".") else "." + ext

    @staticmethod
    def _resolve_auto_extension(
            image: MedicalImage,
            fallback: str,
    ) -> str:
        """
        Derive the extension for an image in auto mode.

        Tries, in order:

        1. ``image.metadata["extension"]``
        2. ``image.metadata["format"]`` mapped to a known extension
        3. ``image.path`` (if the attribute exists)
        4. ``fallback``

        Parameters
        ----------
        image : MedicalImage
            Image whose extension should be inferred.
        fallback : str
            Extension to use when nothing else is found.

        Returns
        -------
        str
            Normalized extension starting with ``"."``.
        """
        metadata = getattr(image, "metadata", None) or {}

        ext = metadata.get("extension")
        if ext:
            return IOPipeline._normalize_ext(ext)

        fmt = metadata.get("format")
        if fmt:
            fmt = str(fmt).lower().lstrip(".")
            if fmt == "nifti":
                return ".nii.gz"
            if fmt in {"png", "jpg", "jpeg", "dcm", "nii"}:
                return "." + fmt

        image_path = getattr(image, "path", None)
        if image_path:
            name = Path(image_path).name.lower()
            if name.endswith(".nii.gz"):
                return ".nii.gz"
            suffix = Path(image_path).suffix.lower()
            if suffix:
                return suffix

        return fallback
