import logging
import threading
import os
from typing import Optional

import cv2
from networktables.networktable import NetworkTable

from bucketvision import Resolution, Frame
from bucketvision.fps_logger import FPSLogger

try:
    import networktables
except ImportError:
    pass


class Cv2Capture(threading.Thread):
    """
    This thread continually captures frames from a camera
    """

    def __init__(self, camera_num=0, network_table: NetworkTable = None, exposure: float = None):
        self.logger = logging.getLogger("Cv2Capture{}".format(camera_num))
        self.camera_num = camera_num
        self.net_table = network_table
        self.exposure = exposure

        # Threading Locks
        self.capture_lock = threading.Lock()
        self.frame_lock = threading.Lock()
        self.new_frame_event = threading.Event()

        self.stopped = True

        # open up the camera
        self._open_capture()

        self.camera_res = self.get_camera_resolution()
        self.frame: Optional[Frame] = None

        threading.Thread.__init__(self)

    def _open_capture(self):
        """Open up the camera so we can begin capturing frames"""
        # create the capture object and set settings on the camera
        self.capture = cv2.VideoCapture()
        self.capture.open(self.camera_num)
        self.capture_open = self.capture.isOpened()
        if self.capture_open:
            self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            self.camera_res = (self.capture.get(cv2.CAP_PROP_FRAME_WIDTH), self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if self.exposure is not None:
                self.set_camera_exposure(self.exposure)
        else:
            self.capture_open = False
            self.write_table_value("Camera{}Status".format(self.camera_num),
                                   "Failed to open camera {}!".format(self.camera_num),
                                   level=logging.CRITICAL)

    def next_frame(self) -> Optional[Frame]:
        """
        Return the next frame, when available
        This will reset the new_frame attribute to false
        """
        with self.frame_lock:
            # For maximum thread (or process) safety, you should copy the frame, but this is very expensive
            return self.frame

    def get_camera_resolution(self) -> Optional[Resolution]:
        if self.capture_open:
            with self.capture_lock:
                return Resolution(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH), self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        else:
            return None

    def set_camera_resolution(self, res: Resolution) -> None:
        if self.capture_open:
            with self.capture_lock:
                self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, int(res.width))
                self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, int(res.height))
            self.write_table_value("Width", int(res.width))
            self.write_table_value("Height", int(res.height))
        else:
            self.write_table_value("Camera{}Status".format(self.camera_num),
                                   f"Failed to set resolution to ({res.width}, {res.height})!",
                                   level=logging.CRITICAL)

    def set_camera_exposure(self, exposure: float) -> None:
        self.exposure = exposure
        if self.capture_open:
            with self.capture_lock:
                if os.name == 'nt':
                    # self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1) # must disable auto exposure explicitly on some platforms
                    self.capture.set(cv2.CAP_PROP_EXPOSURE, exposure)
                else:
                    os.system("v4l2-ctl -c exposure_absolute={} -d {}".format(exposure, self.camera_num))
                    print("!! Exposure set to: {}".format(exposure))
            self.write_table_value("Exposure", exposure)
        else:
            self.write_table_value("Camera{}Status".format(self.camera_num),
                                   "Failed to set exposure to {}!".format(exposure),
                                   level=logging.CRITICAL)

    def write_table_value(self, name, value, level=logging.DEBUG):
        self.logger.log(level, "{}:{}".format(name, value))
        if self.net_table is None:
            self.net_table = dict()
        if type(self.net_table) is dict:
            self.net_table[name] = value
        else:
            self.net_table.putValue(name, value)

    def stop(self):
        self.stopped = True

    def start(self):
        self.stopped = False
        threading.Thread.start(self)

    def run(self):
        capture_fps_logger = FPSLogger(f"\nCamera{self.camera_num} Capture")
        first_frame = True
        while not self.stopped:
            # TODO: MAke this less crust, I would like to setup a callback
            try:
                net_table_exposure = self.net_table.getEntry("Exposure").value
                if self.exposure != net_table_exposure:
                    self.set_camera_exposure(net_table_exposure)
            except:
                pass

            # lock any camera operations while we read from the camera
            with self.capture_lock:
                # capture the next image
                _, img = self.capture.read()

            # lock the frame so we can update it with the image from the camera
            with self.frame_lock:
                # set the frame var to the img we just captured
                self.frame = Frame(self.camera_res, self.exposure, img)

                # tell any threads waiting for a new frame that we have one
                self.new_frame_event.set()
                self.new_frame_event.clear()

                if first_frame:
                    first_frame = False
                    print(self.frame.image_data.shape)

            capture_fps_logger.log_frame()


if __name__ == '__main__':
    import os
    from networktables import NetworkTables

    logging.basicConfig(level=logging.DEBUG)

    NetworkTables.initialize(server='localhost')

    VisionTable = NetworkTables.getTable("BucketVision")
    VisionTable.putString("BucketVisionState", "Starting")
    FrontCameraTable = VisionTable.getSubTable('FrontCamera')

    print("Starting Capture")
    camera = Cv2Capture(network_table=FrontCameraTable)
    camera.start()

    # os.system("v4l2-ctl -c exposure_absolute={}".format(configs['brightness']))

    print("Getting Frames")
    while True:
        # camera.new_frame.wait()
        frame = camera.next_frame()
        if frame is not None:
            cv2.imshow('my webcam', frame.image_data)
        if cv2.waitKey(1) == 27:
            break  # esc to quit
    camera.stop()
