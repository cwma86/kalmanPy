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
  def __init__(self) -> None:
    pass

  def ProcessTrack(self, request, context):
    for i in range(len(request.tracks)):
      track = measurement_pb2.track()
      track.ParseFromString(request.tracks[i])

      print(f"received velocity of x: {track.x_velocity}")
      print(f"received velocity of y: {track.y_velocity}")
      print(f"received velocity of z: {track.z_velocity}")
      print(f"using : {len(track.measurements)} measurements")
    return google_dot_protobuf_dot_empty__pb2.Empty()


def serve(args):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    measurement_pb2_grpc.add_TrackProducerServicer_to_server(TrackWriter(), 
                                                             server)
    server.add_insecure_port('[::]:' + str(args.recvport))
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
  args = input_args()
  serve(args)