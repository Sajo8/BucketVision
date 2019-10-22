import argparse
import logging
import threading
from typing import List

import cv2
from networktables import NetworkTables
from networktables.networktable import NetworkTable

from bucketvision.capturers.cv2capture import Cv2Capture
from bucketvision.configs import configs
from bucketvision.displays.cameraserverdisplay import CameraServerDisplay
from bucketvision.displays.cv2display import Cv2Display
from bucketvision.multiplexers.capture_source_mux import CaptureSourceMux
from bucketvision.multiplexers.output_mux_1_to_n import OutputMux1toN
from bucketvision.postprocessors.angryprocessor import AngryProcessor
from bucketvision.sourceprocessors.overlaysource import OverlaySource
from bucketvision.sourceprocessors.resizesource import ResizeSource

logging.basicConfig(level=logging.DEBUG)


def connectionListener(connected, info):
    """ used to wait till network tables is initalized """
    print(info, '; Connected=%s' % connected)
    with cond:
        notified[0] = True
        cond.notify()


if __name__ == '__main__':
    # add parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('-ip', '--ip-address', required=False, default='10.41.83.2',
                        help='IP Address for NetworkTable Server')

    parser.add_argument('-t', '--test', help='Test mode (uses cv2 display)', action='store_true')

    parser.add_argument('-cam', '--num-cam', required=False, default=1,
                        help='Number of cameras to instantiate', type=int, choices=range(1, 10))
    parser.add_argument('-co', '--offs-cam', required=False, default=0,
                        help='First camera index to instantiate', type=int, choices=range(0, 10))

    parser.add_argument('-proc', '--num-processors', required=False, default=4,
                        help='Number of processors to instantiate', type=int, choices=range(0, 10))

    args = parser.parse_args()

    cond = threading.Condition()
    notified = [False]
    # init networktables
    NetworkTables.initialize(server=args.ip_address)
    # add a listener for connection
    NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

    # if not connected then block and wait
    with cond:
        print("Waiting")
        if not notified[0]:
            cond.wait()

    vision_table: NetworkTable = NetworkTables.getTable("BucketVision")
    vision_table.putString("BucketVisionState", "Starting")
    vision_table.putNumber("Exposure", 50.0)

    # create a source per camera
    capture_sources: List[Cv2Capture] = list()
    for i in range(args.num_cam):
        cap = Cv2Capture(camera_num=i + args.offs_cam, network_table=vision_table, exposure=0.01,
                         res=configs['camera_res'])
        capture_sources.append(cap)
        cap.start()
        cap.exposure = 10

    # send each source through our source processors
    # these do things like resize the image and draw a simple center line
    capture_source_mux = CaptureSourceMux(capture_sources)
    output_mux = OutputMux1toN(capture_source_mux)
    process_output = output_mux.create_output()
    display_output = OverlaySource(ResizeSource(output_mux.create_output(), res=configs['output_res']))

    vision_table.putString("BucketVisionState", "Started Capture")

    # create post processor threads to process each image before sending it to the CameraServer (or window if testing)
    # this does the more complex target finding. We create multiple process threads to process the frames
    # as they are captured
    proc_list: List[AngryProcessor] = list()
    for i in range(args.num_processors):
        proc = AngryProcessor(process_output, network_table=vision_table, debug_label="Proc{}".format(i))
        proc_list.append(proc)
        proc.start()

    vision_table.putString("BucketVisionState", "Started Process")

    if args.test:
        window_display = Cv2Display(source=display_output)
        window_display.start()
        vision_table.putString("BucketVisionState", "Started CV2 Display")
    else:
        cs_display = CameraServerDisplay(source_processor=display_output, network_table=vision_table)
        cs_display.start()
        vision_table.putString("BucketVisionState", "Started CS Display")

    try:
        vision_table.putValue("CameraNum", 0)
        while True:
            capture_source_mux.source_num = int(vision_table.getEntry("CameraNum").value)
            if args.test:
                if window_display._new_frame:
                    cv2.imshow(window_display.window_name, window_display._frame)
                    window_display._new_frame = False
                cv2.waitKey(1)

    except KeyboardInterrupt:
        pass
    finally:
        if args.test:
            window_display.stop()
            cv2.destroyAllWindows()
        else:
            cs_display.stop()
        for proc in proc_list:
            proc.stop()
        for cap in capture_sources:
            cap.stop()
