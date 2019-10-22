import logging
import threading
from typing import Tuple, Optional

from cscore import CameraServer
from networktables.networktable import NetworkTable

from bucketvision.configs import configs
from bucketvision.sourceprocessors.source_processor import SourceProcessor


class CameraServerDisplay(threading.Thread):
    """
    This displays output to the CameraServer (i.e. you are running on the robot)
    """
    colors = [
        (75, 25, 230),
        (25, 225, 255),
        (200, 130, 0),
        (48, 130, 245),
        (240, 240, 70),
        (230, 50, 240),
        (190, 190, 250),
        (128, 128, 0),
        (255, 190, 230),
        (40, 110, 170),
        (200, 250, 255),
        (0, 0, 128),
        (195, 255, 170),
        (128, 0, 0),
        (128, 128, 128),
        (255, 255, 255),
        (75, 180, 60)
    ]

    def __init__(self, source_processor: Optional[SourceProcessor] = None, stream_name="Camera0", res: Tuple[int, int] = None, network_table: NetworkTable = None):
        self.logger = logging.getLogger("CSDisplay")
        self.stream_name = stream_name
        self.source_processor = source_processor
        if res is not None:
            self.output_width = res[0]
            self.output_height = res[1]
        else:
            if self.source_processor is not None:
                self.output_width = int(self.source_processor.source_width)
                self.output_height = int(self.source_processor.source_height)

        cs = CameraServer.getInstance()
        self.outstream = cs.putVideo(self.stream_name, self.output_width, self.output_height)

        self.frame = None
        self.new_frame = False

        self.net_table = network_table

        self.stopped = True
        threading.Thread.__init__(self)

    def update_frame(self, img):
        """Manually update the cameraserver frame. This is only used by the main() function below"""
        self.frame = img
        self.new_frame = True

    def stop(self):
        self.stopped = True

    def start(self):
        self.stopped = False
        threading.Thread.start(self)

    @staticmethod
    def NetTableVisionGet(net_table):
        array_keys = ('angle', 'parallax', 'distance', 'pos_x', 'pos_y', 'size')
        ret_data = dict()
        ret_data['LastFrameTime'] = net_table.getNumber("LastFrameTime", None)
        ret_data['CurrFrameTime'] = net_table.getNumber("CurrFrameTime", None)
        ret_data['NumTargets'] = int(net_table.getNumber("NumTargets", 0))
        for key in array_keys:
            ret_data[key] = net_table.getNumberArray(key, None)
        return ret_data

    def drawtargets(self, image):
        """
        Not currently used...
        :param image:
        :return:
        """
        if self.net_table is None:
            return image
        if self.net_table.getBoolean('Overlay', False):
            return image

        height, width, _ = image.shape
        targets = self.NetTableVisionGet(self.net_table)
        print("CSD: looping {}".format(targets['NumTargets']))
        for index in range(targets['NumTargets']):
            try:
                color = self.colors[index]
                x, y = targets['pos_x'][index], targets['pos_y'][index]
                image = cv2.circle(image, (int(x * width), int(y * height)),
                                   int((targets['size'][index] * width) / 4),
                                   color, -1)
            except IndexError:
                # More targets than colors!
                return image
        return image

    def run(self):
        while not self.stopped:
            if self.source_processor is None:
                # if we have no source processor, just put the frames straight to the output
                if self.new_frame:
                    self.outstream.putFrame(self.frame)
                    self.new_frame = False
            elif self.source_processor.has_new_frame():
                self.outstream.putFrame(self.source_processor.process_frame())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    sink = CameraServerDisplay(res=configs['output_res'])
    sink.start()

    import cv2

    cam = cv2.VideoCapture(0)
    while True:
        ret_val, img = cam.read()
        sink.update_frame(img)
        # Esc to quit
        if cv2.waitKey(1) == 27:
            break
    sink.stop()
