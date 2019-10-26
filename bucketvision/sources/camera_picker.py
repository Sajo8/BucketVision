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
    
    def next_frame(self):
        return self._get_active_source().next_frame()

    def get_camera_resolution(self):
        return self._get_active_source().get_camera_resolution()

    def wait_for_new_frame(self):
        self._get_active_source().new_frame_event.wait()
