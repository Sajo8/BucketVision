from typing import Tuple

import cv2

from bucketvision.multiplexers.output_mux_1_to_n import DelegatedSource
from bucketvision.sourceprocessors.source_processor import SourceProcessor


class ResizeSource(SourceProcessor):
    """
    This resizes the source image to our target resolution (i.e. 320x200)
    """

    def __init__(self, source: DelegatedSource, res: Tuple[int, int] = None) -> None:
        SourceProcessor.__init__(self, source, res)

    def process_frame(self):
        # resize this frame
        return cv2.resize(self.source.next_frame(), (int(self.source_width), int(self.source_height)))
