import logging

import Inst_Vel_Tracker as ivt
import Kalman_Filter_Tracker as kft
import measurement_pb2

class TrackManager:
  def __init__(self, filter_type='kft') -> None:
    if filter_type == 'kft':
      self.track_int =  kft.Kalman_Filter_Tracker()
      logging.info(f"Running tracker as Kalman filter")
    elif filter_type == 'ivt':
      self.track_int =  ivt.Inst_Vel_Tracker()
      logging.info(f"Running tracker as instant velocity tracker")
    else:
      logging.error(f"Invalid tracker filter type selction {filter_type}")

    self.filter = filter_type
    self.Tracks = []
    
  def process_measurement(self, request):
    tracks = []
    for i in range(len(request.measurements)):
      measurement = measurement_pb2.measurement()
      measurement.ParseFromString(request.measurements[i])
      tracks.append(self.track_int.add_measurement(measurement).SerializeToString())
    
    track_grp =  measurement_pb2.track_group(tracks=tracks)
    return track_grp