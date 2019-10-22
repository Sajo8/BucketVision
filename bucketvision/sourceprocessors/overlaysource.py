from typing import Tuple

import cv2

from bucketvision.sourceprocessors.source_processor import SourceProcessor


class OverlaySource(SourceProcessor):
    """
    This overlays the source image with a green line
    """

    def __init__(self, source: SourceProcessor, res: Tuple[int, int] = None) -> None:
        SourceProcessor.__init__(self, source, res)

    def process_frame(self):
        # draw a green line down the middle
        return cv2.line(self.source.process_frame(), (int(self.source_width // 2), int(self.source_height)),
                        (int(self.source_width // 2), 0), (0, 255, 0), 2)
