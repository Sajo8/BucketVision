from typing import Any

import cv2
import numpy as np

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

    colors = [
        (75, 25, 230),
        (25, 225, 255),
        (200, 130, 0),
        (48, 130, 245),
        (240, 240, 70),
        (230, 50, 240),
        (190, 190, 250),
        (128, 128, 0),
        (255, 190, 230),
        (40, 110, 170),
        (200, 250, 255),
        (0, 0, 128),
        (195, 255, 170),
        (128, 0, 0),
        (128, 128, 128),
        (255, 255, 255),
        (75, 180, 60)
    ]

    def __init__(self, target_finder: TargetFinder):
        super().__init__()
        self.target_finder = target_finder
        self.processor = ProcessImage()

    def process_frame(self, frame: Frame) -> Frame:
        frame.image_data = self.draw_targets(frame.image_data)
        return frame

    def draw_targets(self, image) -> Any:
        height, width, _ = image.shape
        for index, target in enumerate(self.target_finder.vision_targets):
            found_cont = [np.int0(cv2.boxPoints(r)) for r in [target.l_rect.raw_rect, target.r_rect.raw_rect]]
            try:
                color = TargetSourceProcessor.colors[index]
                image = cv2.drawContours(image, found_cont, -1, color, 3)
                x, y = target.pos
                image = cv2.circle(image, (int(x * width), int(y * height)),
                                   int((target.size * width) / 4),
                                   color, -1)
            except IndexError:
                # More targets than colors!
                pass
        return image
