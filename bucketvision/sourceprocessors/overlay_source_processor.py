import cv2

from bucketvision import Frame
from bucketvision.sourceprocessors.source_processor import SourceProcessor


class OverlaySourceProcessor(SourceProcessor):
    """
    This overlays the source image with a green line
    """

    def process_frame(self, frame: Frame) -> Frame:
        # draw a green line down the middle
        frame.image_data = cv2.line(
            img=frame.image_data,
            pt1=(int(frame.res.width // 2), int(frame.res.height)),
            pt2=(int(frame.res.width // 2), 0),
            color=(0, 255, 0),
            thickness=2)
        return frame
