import logging
import unittest
import os
import sys

TEST_PATH = os.path.dirname(os.path.realpath(__file__))
SOURCE_PATH = os.path.join(
    TEST_PATH,"../../src"
)
sys.path.append(SOURCE_PATH)
sys.path.append(os.path.join(SOURCE_PATH, 'auto_generated'))
sys.path.append(os.path.join(SOURCE_PATH, 'tracker'))
import TrackInterface as ti
import measurement_pb2

logging.basicConfig(
            format='%(asctime)s,%(msecs)d %(levelname)-8s\
                [%(filename)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d:%H:%M:%S',
            level=logging.DEBUG)
xvel_value = 5.0
yvel_value = 6.0
zvel_value = 7.0

class TrackInterfaceTest(ti.TrackInterface):
  def add_measurement(self, 
                      meas: measurement_pb2.measurement):
    track_msg = measurement_pb2.track(x_velocity=xvel_value,
                                  y_velocity=yvel_value,
                                  z_velocity=zvel_value)
    return track_msg

class test_TrackInterface(unittest.TestCase):
  def test_TrackInterfaceTest(self):
    test_interface = TrackInterfaceTest()

    new_meas = measurement_pb2.measurement(x=1.0,
                                        y=2.0,
                                        z=3.0,
                                        time=10)
    new_track = test_interface.add_measurement(new_meas)
    self.assertAlmostEqual(new_track.x_velocity, xvel_value)
    self.assertAlmostEqual(new_track.y_velocity, yvel_value)
    self.assertAlmostEqual(new_track.z_velocity, zvel_value)
    logging.debug(f"test_TrackInterfaceTest pass!")

if __name__ == '__main__':
  unittest.main()