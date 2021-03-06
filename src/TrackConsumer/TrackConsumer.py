#!/usr/bin/env python3
import argparse
import grpc
import logging
import os
import sys

from concurrent import futures

script_path = os.path.dirname(os.path.abspath( __file__ ))
src_dir = os.path.dirname(script_path)
autogen_dir = os.path.join(src_dir,"auto_generated")
sys.path.insert(1, autogen_dir)
import measurement_pb2_grpc
import measurement_pb2

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

def input_args():
  """
    Input argument parser
    ...
  """
  parser = argparse.ArgumentParser(description='Run Tracker')
  parser.add_argument('-r', '--recvport',type=int, default=50052,
                    help='recieve port')
  parser.add_argument('-v', '--verbose', action='store_true',
                    help='Verbose logging')
  args = parser.parse_args()
    # initialize logger format
  logLevel = logging.INFO
  if args.verbose:
    logLevel = logging.DEBUG
  logging.basicConfig(
            format='%(asctime)s,%(msecs)d %(levelname)-2s ' +
                   '[%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logLevel)
  logging.info(f"logging set to {logging.getLevelName(logLevel)}")
  logging.debug(f"Recving data on port {args.recvport}")

  return args

class TrackWriter(measurement_pb2_grpc.TrackProducerServicer):
  """
    A class that functions as a track message group consumer and writes
    track data to files

    Attributes
    -----------
    trackfile: string
      The file path to the location of the file that will store all the track
      message group data

    Methods
    -----------

  ProcessTrack()
    Implementation of the protobuf defined service interface used to consume
    track groups
  """
  def __init__(self, trackfile) -> None:
    self.trackfile = trackfile
    pass

  def ProcessTrack(self, request, context):
    with open(self.trackfile, "a") as myfile:
      logging.info(f"received track group with {len(request.tracks)} tracks, logging to file.")
      for i in range(len(request.tracks)):
        track = measurement_pb2.track()
        track.ParseFromString(request.tracks[i])

        logging.debug(f"received velocity of x: {track.x_velocity}")
        logging.debug(f"received velocity of y: {track.y_velocity}")
        logging.debug(f"received velocity of z: {track.z_velocity}")
        logging.debug(f"using : {len(track.measurements)} measurements")
        myfile.write(f"trk {track.x_pred_pos} {track.y_pred_pos} {track.z_pred_pos} " +
                     f"{track.x_velocity} {track.y_velocity} {track.z_velocity} {track.track_id}\n")
        for i in range(len(track.measurements)):
          meas = measurement_pb2.measurement()
          meas.ParseFromString(track.measurements[i])

          myfile.write(f"meas {meas.x} " +
                       f"{meas.y} " +
                       f"{meas.z} " + 
                       f"{meas.true_x} " +
                       f"{meas.true_y} " +
                       f"{meas.true_z}\n")

    return google_dot_protobuf_dot_empty__pb2.Empty()


def serve(args):
    """
      Creates the grpc server for processing track groups
    """
    trackfile = os.path.join(script_path, "track.track" )
    if (os.path.exists(trackfile)):
      os.remove(trackfile)
    with open(trackfile, "w") as myfile:
      myfile.write(f"#trk x_pred_pos y_pred_pos z_pred_pos vel_x vel_y vel_z track_id\n")
      myfile.write(f"#meas x y z true_x true_y true_z\n")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    measurement_pb2_grpc.add_TrackProducerServicer_to_server(TrackWriter(trackfile), 
                                                             server)
    server.add_insecure_port('[::]:' + str(args.recvport))
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
  args = input_args()
  serve(args)