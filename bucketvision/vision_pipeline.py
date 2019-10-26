import cv2
import threading
from typing import List, Optional

from bucketvision import Resolution, Frame
from bucketvision.fps_logger import FPSLogger
from bucketvision.sources.camera_picker import CameraPicker
from bucketvision.sourceprocessors.source_processor import SourceProcessor
from bucketvision.publisher import Publisher


class VisionPipeline(threading.Thread, Publisher):
    """
    A vision pipeline takes a set of Camera captures as inputs
    and a series of processors that will process the image

    It also publishes frame update events whenever the camera has a new frame
    to process
    """

    def __init__(self, sources: CameraPicker, processors: List[SourceProcessor] = []) -> None:
        threading.Thread.__init__(self)
        Publisher.__init__(self)
        self.cameras = sources
        self.processors = processors

        self.last_frame: Optional[Frame] = None
        self.stopped = True

        self.output_resolution = self.cameras.get_camera_resolution()

    def add_source_processor(self, processor: SourceProcessor):
        self.processors.append(processor)

    def stop(self):
        self.stopped = True

    def start(self):
        self.stopped = False
        threading.Thread.start(self)

    def run(self):
        capture_fps_logger = FPSLogger("VisionPipeline Capture")
        process_fps_logger = FPSLogger("VisionPipeline Process")
        while not self.stopped:
            # wait for the next frame
            self.cameras.wait_for_new_frame()

            # log our FPS for capturing images
            capture_fps_logger.log_frame()

            # if our camera has a new frame, grab it and process it
            frame = self.cameras.next_frame()

            # send the frame through each source processor
            for processor in self.processors:
                frame = processor.process_frame(frame)


            # log our FPS for processing images
            process_fps_logger.log_frame()

            # we are done processing, set the last_frame field and publish
            # an updated frame to any subscribers
            self.last_frame = frame
            self.publish_frame_update(frame)


if __name__ == '__main__':
    from networktables import NetworkTables
    from bucketvision.sources.cv2capture import Cv2Capture
    from bucketvision.sourceprocessors.resize_source_processor import ResizeSourceProcessor

    NetworkTables.initialize(server='localhost')

    vision_table = NetworkTables.getTable("BucketVision")
    vision_table.putString("BucketVisionState", "Starting")
    front_camera_table = vision_table.getSubTable('FrontCamera')

    print("Starting Capture")
    camera = Cv2Capture(network_table=front_camera_table)
    camera.start()

    # create a simple pipeline with a source and two processors
    pipeline = VisionPipeline(
        CameraPicker([camera]),
        [
            ResizeSourceProcessor(Resolution(320, 200)),
        ]
    )

    # this is a bit of a hack, but we need to register a callback for
    # when a new frame has been processed. We make a simple function
    # to just update the new_frame_available boolean
    new_frame_available = False


    def on_update(frame: Frame) -> None:
        global new_frame_available
        new_frame_available = True


    # add the on_update function we defined above as a subscriber
    pipeline.add_subscriber(on_update)

    # start the pipeline. It is a thread that grabs new images from
    # the camera when they are available and processes them
    pipeline.start()

    while True:
        if new_frame_available:
            new_frame_available = False
            # Note: on OSX you can only update UI windows on the main thread which is
            # why we grab the image data to show here
            if pipeline.last_frame is not None:
                cv2.imshow('VisionPipelineTest', pipeline.last_frame.image_data)
        if cv2.waitKey(1) == 27:
            break  # esc to quit

    camera.stop()
    pipeline.stop()
