import cv2
import threading
from typing import List

from bucketvision import Resolution, Frame
from bucketvision.sources.capture_source_mux import CaptureSourceMux
from bucketvision.sourceprocessors.source_processor import SourceProcessor
from bucketvision.publisher import Publisher


class VisionPipeline(threading.Thread, Publisher):
    """
    A vision pipeline takes a set of Camera captures as inputs
    and a series of processors that will process the image

    It also can be registered with outputs to be called
    when there is a new frame
    """

    def __init__(self, sources: CaptureSourceMux, processors: List[SourceProcessor]=[], output_resolution: Resolution=None) -> None:
        threading.Thread.__init__(self)
        Publisher.__init__(self)
        self.sources = sources
        self.processors = processors

        self.last_frame: Frame = None
        self.stopped = True

        if output_resolution is None:
            self.output_resolution = output_resolution
        else:
            self.output_resolution = self.sources.get_camera_resolution()

    def stop(self):
        self.stopped = True

    def start(self):
        self.stopped = False
        threading.Thread.start(self)

    def run(self):
        while not self.stopped:
            if self.sources.has_new_frame():
                frame = self.sources.next_frame()
                for processor in self.processors:
                    frame = processor.process_frame(frame)

                self.last_frame = frame
                self.publish_frame_update(self, frame)


if __name__ == '__main__':
    from networktables import NetworkTables
    from bucketvision.sources.cv2capture import Cv2Capture
    from bucketvision.postprocessors.target_finder import TargetFinder
    from bucketvision.sourceprocessors.overlay_source_processor import OverlaySourceProcessor
    from bucketvision.sourceprocessors.resize_source_processor import ResizeSourceProcessor
    from bucketvision.sourceprocessors.target_source_processor import TargetSourceProcessor

    NetworkTables.initialize(server='localhost')

    vision_table = NetworkTables.getTable("BucketVision")
    vision_table.putString("BucketVisionState", "Starting")
    front_camera_table = vision_table.getSubTable('FrontCamera')

    print("Starting Capture")
    camera = Cv2Capture(network_table=front_camera_table)
    camera.start()

    target_finder = TargetFinder(vision_table)

    # create a simple pipeline with a source and two processors
    pipeline = VisionPipeline(
        CaptureSourceMux([camera]),
        [
            ResizeSourceProcessor(Resolution(320, 200)),
            OverlaySourceProcessor(),
            TargetSourceProcessor(target_finder)
        ]
    )

    # this is a bit of a hack, but we need to register a callback for
    # when a new frame has been processed. We make a simple function
    # to just update the new_frame_available boolean
    new_frame_available = False


    def on_update(pipeline: VisionPipeline, frame: Frame) -> None:
        global new_frame_available
        new_frame_available = True

    # register the on_update function we made above with the target
    # finder because it contains the final output we want
    target_finder.add_subscriber(on_update)
    target_finder.start()

    # register the target finder as an output of the pipeline
    pipeline.add_subscriber(target_finder.on_frame_update)
    # start the pipeline. It is a thread that grabs new images from
    # the camera when they are available and processes them
    pipeline.start()

    while True:
        if new_frame_available:
            new_frame_available = False
            # Note: on OSX you can only update UI windows on the main thread which is
            # why we grab the image data to show here
            cv2.imshow('VisionPipelineTest', pipeline.last_frame.image_data)
        if cv2.waitKey(1) == 27:
            break  # esc to quit

    camera.stop()
    pipeline.stop()
    target_finder.stop()
