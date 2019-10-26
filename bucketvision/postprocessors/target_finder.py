import threading
from typing import List, Optional

from networktables.networktable import NetworkTable

from bucketvision import Frame
from bucketvision.fps_logger import FPSLogger
from bucketvision.postprocessors.process_image import VisionTarget, ProcessImage


class TargetFinder(threading.Thread):
    """
    The TargetFinder will be an output to a pipeline
    It is registered with a Pipeline for any new images that are
    available. When a new image is available it will find targets on it
    and update network tables
    """
    processor = ProcessImage()

    @staticmethod
    def dict_zip(*dicts):
        all_keys = {k for d in dicts for k in d.keys()}
        return {k: [d[k] for d in dicts if k in d] for k in all_keys}

    @staticmethod
    def frame_processor(frame: Frame) -> List[VisionTarget]:
        # process the frame
        return TargetFinder.processor.find_target(frame.image_data)

    def __init__(self, network_table: NetworkTable = None) -> None:
        threading.Thread.__init__(self)
        self.network_table = network_table

        # setup some defaults
        self.stopped = True

        self.currently_processing_frame: Optional[Frame] = None
        self.next_frame: Optional[Frame] = None

        self.vision_targets_lock = threading.Lock()
        self._vision_targets: List[VisionTarget] = list()

    @property
    def vision_targets(self):
        with self.vision_targets_lock:
            return self._vision_targets

    def on_frame_update(self, frame: Frame):
        """
        This callback is registered with a VisionPipeline to be called
        when the vision pipeline has a new frame
        """
        if self.next_frame != frame:
            self.next_frame = frame

    def _update_network_table(self) -> None:
        # Update the network table with targets
        if self.network_table is not None:
            result_data = self.dict_zip(*[r.dict() for r in self._vision_targets])
            self.network_table.putNumber("NumTargets", len(self._vision_targets))
            for key, value in result_data.items():
                # Here we assume that every param is a number of some kind
                self.network_table.putNumberArray(key, value)

    def stop(self) -> None:
        self.stopped = True

    def start(self) -> None:
        self.stopped = False
        threading.Thread.start(self)

    def run(self) -> None:
        process_fps_logger = FPSLogger(f"TargetFinder Process")
        while not self.stopped:
            if self.next_frame != self.currently_processing_frame:
                self.currently_processing_frame = self.next_frame

                if self.currently_processing_frame is not None:
                    # find new targets
                    new_vision_targets = TargetFinder.frame_processor(self.currently_processing_frame)
                    with self.vision_targets_lock:
                        self._vision_targets = new_vision_targets

                    process_fps_logger.log_frame()
                    self._update_network_table()


