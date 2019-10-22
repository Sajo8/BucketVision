from typing import Tuple, Union

from bucketvision.sourceprocessors.delegated_source import DelegatedSource


class SourceProcessor:
    """
    This is a base class for the resize and overlay source processors we have
    """

    def __init__(self, source: Union['SourceProcessor', DelegatedSource], res: Tuple[int, int] = None) -> None:
        self.source = source
        if res is not None:
            self.source_width = res[0]
            self.source_height = res[1]
        else:
            self.source_width = int(self.source.source_width)
            self.source_height = int(self.source.source_height)

    def process_frame(self) -> None:
        raise NotImplementedError("Subclasses of SourceProcessor must implement process_frame() method")

    @property
    def source_width(self) -> int:
        return self.source.source_width

    @source_width.setter
    def source_width(self, val: int) -> None:
        self.source.source_width = val

    @property
    def source_height(self) -> int:
        return self.source.source_height

    @source_height.setter
    def source_height(self, val: int) -> None:
        self.source.source_height = val

    def has_new_frame(self) -> bool:
        return self.source.has_new_frame()
