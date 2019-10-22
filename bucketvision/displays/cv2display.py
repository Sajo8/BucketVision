import logging
import threading
from typing import Union

import cv2

from bucketvision.postprocessors.angryprocessor import AngryProcessor
from bucketvision.sourceprocessors.source_processor import SourceProcessor


class Cv2Display(threading.Thread):
    """
    This displays output to a cv2 window (i.e. you are testing locally)
    """

    def __init__(self, source: Union[SourceProcessor, AngryProcessor] = None, window_name="Camera0"):
        self.logger = logging.getLogger("Cv2Display")
        self.window_name = window_name
        self.source = source

        self._frame = None
        self._new_frame = False

        self.stopped = True
        threading.Thread.__init__(self)

    @property
    def frame(self):
        return self._frame

    @frame.setter
    def frame(self, img):
        self._frame = img
        self._new_frame = True

    def stop(self):
        self.stopped = True

    def start(self):
        self.stopped = False
        threading.Thread.start(self)

    def run(self):
        while not self.stopped:
            if self.source is not None:
                if self.source.has_new_frame():
                    self.frame = self.source.process_frame()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    sink = Cv2Display()
    sink.start()

    cam = cv2.VideoCapture(0)
    while True:
        ret_val, img = cam.read()
        sink.frame = img
        # Esc to quit
        if cv2.waitKey(1) == 27:
            break
