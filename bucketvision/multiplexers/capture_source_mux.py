from typing import List

from bucketvision.capturers.cv2capture import Cv2Capture


class CaptureSourceMux:
    """
    This multiplexer takes captures from the camera as sources
    """

    def __init__(self, capture_sources: List[Cv2Capture]):
        self.sources = capture_sources
        self.source_num = 0

    def _get_active_source(self) -> Cv2Capture:
        return self.sources[self.source_num]
    
    def has_new_frame(self) -> bool:
        return self._get_active_source().new_frame

    def set_new_frame(self, val: bool) -> None:
        self._get_active_source().new_frame = val

    def next_frame(self):
        return self._get_active_source().next_frame()

    @property
    def width(self):
        return self._get_active_source().width

    @width.setter
    def width(self, val: int) -> None:
        self._get_active_source().width = val

    @property
    def height(self):
        return self._get_active_source().height

    @height.setter
    def height(self, val: int) -> None:
        self._get_active_source().height = val

    @property
    def exposure(self):
        return self._get_active_source().exposure

    @exposure.setter
    def exposure(self, val: int) -> None:
        self._get_active_source().exposure = val
