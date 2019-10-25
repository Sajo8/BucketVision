from typing import Any

import cv2

from bucketvision import Resolution, Frame
from bucketvision.sourceprocessors.source_processor import SourceProcessor


class ResizeSourceProcessor(SourceProcessor):
    """
    This resizes the source image to our target resolution (i.e. 320x200)
    """

    def __init__(self, res: Resolution) -> None:
        super().__init__()
        self.res = res

    def process_frame(self, frame: Frame) -> Frame:
        # resize this frame
        # make sure to set our frame.res that we pass along
        # to the next processor in the pipeline
        frame.res = self.res
        frame.image_data = cv2.resize(
            src=frame.image_data,
            dsize=(int(self.res.width), int(self.res.height))
        )
        return frame

