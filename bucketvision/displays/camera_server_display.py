import logging

import cv2
from cscore import CameraServer

from bucketvision import Frame, Resolution
from bucketvision.configs import configs
from bucketvision.vision_pipeline import VisionPipeline

log = logging.getLogger(__file__)


class CameraServerDisplay:
    """
    This displays output to the CameraServer (i.e. a webpage at http://localhost:1181
    """

    def __init__(self, output_resolution: Resolution, stream_name="Camera0") -> None:

        self.stream_name = stream_name

        self.output_resolution = output_resolution

        # create and start a CameraServer
        cs = CameraServer.getInstance()
        self.out_stream = cs.putVideo(self.stream_name, self.output_resolution.width, self.output_resolution.height)

    def on_update(self, pipeline: VisionPipeline, frame: Frame) -> None:
        """
        On update is called by the vision pipeline to let us know
        there is a new frame available from the camera
        """
        self.out_stream.putFrame(frame.image_data)


if __name__ == '__main__':
    from bucketvision.sources.capture_source_mux import CaptureSourceMux
    from bucketvision.sources.cv2capture import Cv2Capture
    logging.basicConfig(level=logging.DEBUG)

    # start a camera server
    camera_server = CameraServerDisplay(res=configs['output_res'])

    # start capturing input
    camera = Cv2Capture()
    camera.start()

    # make a pipeline with no source processors
    pipeline = VisionPipeline(CaptureSourceMux([camera]))
    pipeline.add_subscriber(camera_server.on_update)
    pipeline.start()

    try:
        # loop forever
        while True:
            # Esc to quit
            if cv2.waitKey(1) == 27:
                break
    finally:
        camera.stop()
        pipeline.stop()
