import threading
import time
from typing import List, Optional

from networktables.networktable import NetworkTable

from bucketvision import Frame
from bucketvision.postprocessors.process_image import VisionTarget, ProcessImage
from bucketvision.publisher import Publisher
from bucketvision.vision_pipeline import VisionPipeline


class TargetFinder(threading.Thread, Publisher):
    """
    The TargetFinder will be an output to a pipeline
    It is registered with a Pipeline for any new images that are
    available. When a new image is available it will find targets on it
    and update network tables
    """

    def __init__(self, network_table: NetworkTable = None) -> None:
        threading.Thread.__init__(self)
        Publisher.__init__(self)
        self.network_table = network_table

        # setup some defaults
        self.stopped = True
        self.new_frame_available = False
        self.last_frame_time = 0.0
        self.next_frame: Optional[Frame] = None

        self.processor = ProcessImage()

        self.results: List[VisionTarget] = list()

    def on_frame_update(self, frame: Frame):
        """
        This callback is registered with a VisionPipeline to be called
        when the vision pipeline has a new frame
        """
        self.next_frame = frame
        self.new_frame_available = True

    @staticmethod
    def dict_zip(*dicts):
        all_keys = {k for d in dicts for k in d.keys()}
        return {k: [d[k] for d in dicts if k in d] for k in all_keys}

    def _update_network_table(self) -> None:
        # Update the network table with targets
        if self.network_table is not None:
            self.network_table.putNumber("LastFrameTime", self.last_frame_time)
            self.network_table.putNumber("CurrFrameTime", time.time())
            result_data = self.dict_zip(*[r.dict() for r in self.results])
            self.network_table.putNumber("NumTargets", len(self.results))
            for key, value in result_data.items():
                # Here we assume that every param is a number of some kind
                self.network_table.putNumberArray(key, value)

    def stop(self) -> None:
        self.stopped = True

    def start(self) -> None:
        self.stopped = False
        threading.Thread.start(self)

    def run(self) -> None:
        frame_hist: List[float] = list()
        self.last_frame_time = time.time()
        while not self.stopped:
            if self.new_frame_available:
                self.new_frame_available = False
                if len(frame_hist) == 30:
                    print("TargetFinder :{:.1f}fps ".format(1 / (sum(frame_hist) / len(frame_hist))))
                    frame_hist = list()

                self.process_frame()
                self._update_network_table()
                if self.next_frame is not None:
                    self.publish_frame_update(self.next_frame)

                # update some stats
                duration = time.time() - self.last_frame_time
                self.last_frame_time = time.time()
                frame_hist.append(duration)

    def process_frame(self) -> None:
        if self.next_frame is not None:
            self.results = self.processor.find_target(self.next_frame.image_data)
