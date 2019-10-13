import logging
import argparse

import threading
from networktables import NetworkTables

from bucketvision.threads.cv2capture import Cv2Capture
from bucketvision.threads.cv2display import Cv2Display
from bucketvision.threads.angryprocessor import AngryProcessor
from bucketvision.multiplexers.class_mux import ClassMux
from bucketvision.multiplexers.mux1n import Mux1N
from bucketvision.sources.resizesource import ResizeSource
from bucketvision.sources.overlaysource import OverlaySource

from bucketvision.configs import configs

logging.basicConfig(level=logging.DEBUG)


# used to wait till network tables is initalized
def connectionListener(connected, info):
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

    args = vars(parser.parse_args())

    # don't run in test mode if not specified
    if not args['test']:
        from bucketvision.threads.csdisplay import CSDisplay

    cond = threading.Condition()
    notified = [False]
    # init networktables
    NetworkTables.initialize(server=args['ip_address'])
    # add a listener for connection
    NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

    # if not connected then block and wait
    with cond:
        print("Waiting")
        if not notified[0]:
            cond.wait()

    VisionTable = NetworkTables.getTable("BucketVision")
    VisionTable.putString("BucketVisionState", "Starting")
    VisionTable.putNumber("Exposure", 50.0)
    source_list = list()

    for i in range(args['num_cam']):
        cap = Cv2Capture(camera_num=i + args['offs_cam'], network_table=VisionTable, exposure=0.01,
                         res=configs['camera_res'])
        source_list.append(cap)
        cap.start()
        cap.exposure = 10

    source_mux = ClassMux(*source_list)
    output_mux = Mux1N(source_mux)
    process_output = output_mux.create_output()
    display_output = OverlaySource(ResizeSource(output_mux.create_output(), res=configs['output_res']))

    VisionTable.putString("BucketVisionState", "Started Capture")

    proc_list = list()

    for i in range(args['num_processors']):
        proc = AngryProcessor(process_output, network_table=VisionTable, debug_label="Proc{}".format(i))
        proc_list.append(proc)
        proc.start()

    VisionTable.putString("BucketVisionState", "Started Process")

    if args['test']:
        window_display = Cv2Display(source=display_output)
        window_display.start()
        VisionTable.putString("BucketVisionState", "Started CV2 Display")
    else:
        cs_display = CSDisplay(source=display_output, network_table=VisionTable)
        cs_display.start()
        VisionTable.putString("BucketVisionState", "Started CS Display")

    try:
        VisionTable.putValue("CameraNum", 0)
        while True:
            source_mux.source_num = int(VisionTable.getEntry("CameraNum").value)

    except KeyboardInterrupt:
        if args['test']:
            window_display.stop()
        else:
            cs_display.stop()
        for proc in proc_list:
            proc.stop()
        for cap in source_list:
            cap.stop()
