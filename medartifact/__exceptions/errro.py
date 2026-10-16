class ImageLoadError(Exception):
    """Raised when image loading fails."""
    pass


class MedVisionError(Exception):
    pass


class ImageWriteError(MedVisionError):
    pass
