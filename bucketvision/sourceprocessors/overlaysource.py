from typing import Tuple

import cv2

from bucketvision.sourceprocessors.source_processor import SourceProcessor


class OverlaySource(SourceProcessor):
    """
    This overlays the source image with a green line
    """
    def __init__(self, base_source: SourceProcessor, res: Tuple[int, int] = None) -> None:
        SourceProcessor.__init__(self, base_source, res)

    def process_frame(self):
        # draw a green line down the middle
        return cv2.line(self.base_source.process_frame(), (int(self.width // 2), int(self.height)), (int(self.width // 2), 0), (0, 255, 0), 2)
