from typing import Tuple, Union

from bucketvision.sourceprocessors.delegated_source import DelegatedSource


class SourceProcessor:
    """
    This is a base class for the resize and overlay source processors we have
    """
    def __init__(self, base_source: Union['SourceProcessor', DelegatedSource], res: Tuple[int, int] = None) -> None:
        self.base_source = base_source
        if res is not None:
            self.width = res[0]
            self.height = res[1]
        else:
            self.width = int(self.base_source.width)
            self.height = int(self.base_source.height)

    def process_frame(self) -> None:
        raise NotImplementedError("Subclasses of SourceProcessor must implement process_frame() method")

    @property
    def exposure(self) -> int:
        return self.base_source.exposure

    @exposure.setter
    def exposure(self, val: int) -> None:
        self.base_source.exposure = val

    @property
    def width(self) -> int:
        return self.base_source.width

    @width.setter
    def width(self, val: int) -> None:
        self.base_source.width = val

    @property
    def height(self) -> int:
        return self.base_source.height

    @height.setter
    def height(self, val: int) -> None:
        self.base_source.height = val

    @property
    def new_frame(self) -> bool:
        return self.base_source.new_frame
