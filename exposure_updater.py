import os

from networktables import NetworkTables

NetworkTables.initialize(server='10.41.83.2')

VisionTable = NetworkTables.getTable("BucketVision")

while True:
    # calls into video4linux to set the exposure on the cameras over and over again...
    exp = VisionTable.getEntry("Exposure").value
    os.system("v4l2-ctl -c exposure_absolute={} -d {}".format(exp, 0))
    os.system("v4l2-ctl -c exposure_absolute={} -d {}".format(exp, 1))
    print(exp)
