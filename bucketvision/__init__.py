from typing import Any


class Resolution:
    """A simple data class representing width/height resolution"""
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height


class Frame:
    """A frame of image data to be processed or displayed"""
    def __init__(self, res: Resolution, exposure: float, image_data: Any = None):
        self.res = res
        self.exposure = exposure
        self.image_data = image_data
