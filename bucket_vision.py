import argparse
import threading
from typing import List

import cv2

from networktables import NetworkTables
from networktables.networktable import NetworkTable

from bucketvision import Resolution, Frame
from bucketvision.configs import configs
from bucketvision.sources.cv2capture import Cv2Capture
from bucketvision.displays.camera_server_display import CameraServerDisplay
from bucketvision.sources.camera_picker import CameraPicker
from bucketvision.postprocessors.target_finder import TargetFinder
from bucketvision.sourceprocessors.overlay_source_processor import OverlaySourceProcessor
from bucketvision.sourceprocessors.resize_source_processor import ResizeSourceProcessor
from bucketvision.sourceprocessors.target_source_processor import TargetSourceProcessor
from bucketvision.vision_pipeline import VisionPipeline

cond = threading.Condition()
notified = False

# this is a bit of a hack, but we need to register a callback for
# when a new frame has been processed. We make a simple function
# to just update the new_frame_available boolean
new_frame_available = False


def on_update(frame: Frame) -> None:
    global new_frame_available
    new_frame_available = True


def connectionListener(connected, info):
    """ used to wait till network tables is initalized """
    print(info, '; Connected=%s' % connected)
    with cond:
        global notified
        notified = True
        cond.notify()


def init_cameras(num_cameras: int, camera_offset: int, vision_table: NetworkTable):
    """ Initialize 1 or more cameras and start capturing images"""
    cameras: List[Cv2Capture] = list()
    for i in range(num_cameras):
        camera = Cv2Capture(camera_num=i + camera_offset, network_table=vision_table, exposure=.01)
        cameras.append(camera)
        camera.start()
    return cameras


def init_network_tables(args):
    # init networktables (Must launch OutlineViewer if running locally)
    NetworkTables.initialize(server=args.ip_address)
    # add a listener for connection
    NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)
    # if not connected then block and wait
    with cond:
        print("Waiting")
        if not notified:
            cond.wait()
    vision_table = NetworkTables.getTable("BucketVision")
    vision_table.putString("BucketVisionState", "Starting")
    return vision_table


def main():
    # add parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('-ip', '--ip-address', required=False, default='10.41.83.2',
                        help='IP Address for NetworkTable Server')

    parser.add_argument('-t', '--test', help='Test mode (uses cv2 display)', action='store_true')

    parser.add_argument('-cams', '--num-cameras', required=False, default=1,
                        help='Number of cameras to instantiate', type=int, choices=range(1, 10))
    parser.add_argument('-coff', '--camera-offset', required=False, default=0,
                        help='First camera index to instantiate', type=int, choices=range(0, 10))

    args = parser.parse_args()

    # create our network_table we use to pass around args
    vision_table = init_network_tables(args)

    # start capturing from our cameras
    cameras = init_cameras(args.num_cameras, args.camera_offset, vision_table)

    vision_table.putString("BucketVisionState", "Started Capture")

    # create a TargetFinder. We will pass this to a TargetSourceProcessor
    # in the pipeline, so create the TargetFinder first
    target_finder = TargetFinder(vision_table)
    target_finder.start()
    target_source_processor = TargetSourceProcessor(target_finder)

    # create a simple pipeline with the camera sources and a few processors
    pipeline = VisionPipeline(
        CameraPicker(cameras),
        [
            ResizeSourceProcessor(Resolution(320, 200)),
            OverlaySourceProcessor(),
        ]
    )

    vision_table.putString("BucketVisionState", "Started Process")

    cs_display = CameraServerDisplay(configs['output_res'])
    vision_table.putString("BucketVisionState", "Started CS Display")

    # Add three subscribers to the pipeline. These three functions will be called anytime we have a new frame
    pipeline.add_subscriber(target_finder.on_frame_update)
    pipeline.add_subscriber(cs_display.on_update)
    pipeline.add_subscriber(on_update)

    # start the pipeline. It is a thread that grabs new images from
    # the camera when they are available and processes them
    pipeline.start()

    try:
        # grab a reference to the global variable that will be updated by the TargetFinder's update pub
        global new_frame_available
        while True:
            if args.test:
                if new_frame_available:
                    new_frame_available = False
                    # Note: on OSX you can only update UI windows on the main thread which is
                    # why we grab the image data to show here

                    # draw targets before showing the image
                    # TODO: this means the targets won't show up on the camera server...
                    frame = target_source_processor.process_frame(pipeline.last_frame)
                    cv2.imshow('VisionPipelineTest', frame.image_data)
                if cv2.waitKey(1) == 27:
                    break  # esc to quit
    finally:
        for camera in cameras:
            camera.stop()
        pipeline.stop()
        target_finder.stop()


if __name__ == '__main__':
    main()
