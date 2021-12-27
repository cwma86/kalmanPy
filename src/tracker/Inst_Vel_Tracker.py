import numpy as np

import TrackInterface as ti
import measurement_pb2

class Inst_Vel_Tracker(ti.TrackInterface):
  def __init__(self):
      super().__init__()
      self.meas_list = []

  def add_measurement(self, 
                      meas: measurement_pb2.measurement) -> measurement_pb2.track :
    self.print_meas(meas)
    self.meas_list.append(meas)
    pred_vel = np.array([[0],[0],[0]])
    if len(self.meas_list) >= 2:
      dt = self.meas_list[-1].time - self.meas_list[-2].time
      finalmeas = np.array([[self.meas_list[-1].x],
                            [self.meas_list[-1].y],
                            [self.meas_list[-1].z],])

      initmeas = np.array([[self.meas_list[-2].x],
                            [self.meas_list[-2].y],
                            [self.meas_list[-2].z],])
      pred_vel = (finalmeas - initmeas) / dt

    track_msg = measurement_pb2.track(x_velocity=pred_vel[0],
                                      y_velocity=pred_vel[1],
                                      z_velocity=pred_vel[2])
    for i in range(len(self.meas_list)):
      meas =  self.meas_list[i].SerializeToString()
      track_msg.measurements.append(meas)
    return track_msg

