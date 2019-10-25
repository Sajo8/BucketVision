from typing import Any


class Resolution:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height


class Frame:
    """A frame of image data to be processed or displayed"""
    def __init__(self, res: Resolution, exposure: int, image_data: Any = None):
        self.res = res
        self.exposure = exposure
        self.image_data = image_data
