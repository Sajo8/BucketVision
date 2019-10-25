from typing import List

from bucketvision.sources.cv2capture import Cv2Capture


class CameraPicker:
    """
    The CameraPicker switches between the cameras based on the source_num
    Changing the source_num will change which camera we are interacting with
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

    def get_camera_resolution(self):
        return self._get_active_source().get_camera_resolution()
