import logging

import Inst_Vel_Tracker as ivt
import Kalman_Filter_Tracker as kft
import measurement_pb2

class TrackStrategyFactory:
  """
    A class used a configurable interface that can implement
    various tracking strategies to be performed on groups of measurements

    Attributes
    ---------
    track_id: int
      static attribute that can be used to provide unique identifications
      to independant tracks
    track_strategy: trackStrategyInterface()
      an instance of a track strategy implementation. This is used as
      the common interface between various tracking strategies
    
    Methods
    --------
    process_measurement()
      process a measurement group using the configured tracking strategy
  """
  # static track id shared by all instances
  track_id = 1
  def __init__(self, filter_type='kft') -> None:
    if filter_type == 'kft':
      self.track_strategy =  kft.Kalman_Filter_Tracker()
      logging.info(f"Running tracker as Kalman filter")
    elif filter_type == 'ivt':
      self.track_strategy =  ivt.Inst_Vel_Tracker()
      logging.info(f"Running tracker as instant velocity tracker")
    else:
      logging.error(f"Invalid tracker filter type selction {filter_type}")

    self.filter = filter_type
    self.Tracks = []
    
  def process_measurement(self, request):
    tracks = []
    for i in range(len(request.measurements)):
      # For each new measurement in the current measurement group process for new/updated tracks
      measurement = measurement_pb2.measurement()
      measurement.ParseFromString(request.measurements[i])
      track = self.track_strategy.add_measurement(measurement)
      if len(track.measurements) == 1:
        # New track give it a unique ID
        track.track_id = self.track_id
        self.track_id += 1
      print(f"next available track_id {self.track_id}")
      tracks.append(track.SerializeToString())
    logging.info(f"creating track group with {len(tracks)} track messages")
    track_grp =  measurement_pb2.track_group(tracks=tracks)
    return track_grp