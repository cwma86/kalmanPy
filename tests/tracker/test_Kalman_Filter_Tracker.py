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
import Kalman_Filter_Tracker as kft
import measurement_pb2

logging.basicConfig(
            format='%(asctime)s,%(msecs)d %(levelname)-8s\
                [%(filename)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d:%H:%M:%S',
            level=logging.DEBUG)


class test_Kalman_Filter_Tracker(unittest.TestCase):
  def test_Kalman_Filter_TrackerTest(self):
    tracker = kft.Kalman_Filter_Tracker()

    new_meas = measurement_pb2.measurement(x=0.0,
                                        y=1.0,
                                        z=2.0,
                                        time=0)
    new_track = tracker.add_measurement(new_meas)
    self.assertAlmostEqual(new_track.x_velocity, 0.0)
    self.assertAlmostEqual(new_track.y_velocity, 0.0)
    self.assertAlmostEqual(new_track.z_velocity, 0.0)
    self.assertAlmostEqual(len(new_track.measurements) , 1)

    new_meas = measurement_pb2.measurement(x=1.0,
                                        y=3.0,
                                        z=2.5,
                                        time=1)
    new_track = tracker.add_measurement(new_meas)
    logging.debug(f"x_velocity {new_track.x_velocity} y_velocity {new_track.y_velocity} z_velocity {new_track.z_velocity}")
    self.assertAlmostEqual(new_track.x_velocity, 0.55, 2)
    self.assertAlmostEqual(new_track.y_velocity, 1.05, 2)
    self.assertAlmostEqual(new_track.z_velocity, 0.30, 2)
    self.assertAlmostEqual(len(new_track.measurements) , 2)
    logging.debug(f"test_Kalman_Filter_TrackerTest pass!")

if __name__ == '__main__':
  unittest.main()