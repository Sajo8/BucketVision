from typing import Tuple, Any

import cv2

from bucketvision import Frame
from bucketvision.postprocessors.process_image import ProcessImage
from bucketvision.postprocessors.target_finder import TargetFinder
from bucketvision.sourceprocessors.source_processor import SourceProcessor


class TargetSourceProcessor(SourceProcessor):
    """
    This takes any target results from the TargetFinder
    and draws them on the current frame.

    We use this so we always render our targets, even if they are a
    bit behind in processing
    """

    def __init__(self, target_finder: TargetFinder):
        self.target_finder = target_finder
        self.processor = ProcessImage()

    def process_frame(self, frame: Frame) -> Frame:
        frame.image = self.processor.drawtargets(frame.image_data, self.target_finder.results)
        return frame
