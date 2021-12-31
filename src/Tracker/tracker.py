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
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

from TrackManager import TrackManager

def input_args():
  parser = argparse.ArgumentParser(description='Run Tracker')
  parser.add_argument('-r', '--recvport',type=int, default=50051,
                    help='recieve port')
  parser.add_argument('-f', '--filter', default="kft",
                    help='Select tracker filter type' +
                          '  option - description' +
                          '  kft = kalman filter tracker' +
                          '  ivt = instantaneous velocity tracker')
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

class Tracker(measurement_pb2_grpc.MeasurementProducerServicer):
    def __init__(self, stub, filter_type = 'kft') -> None:
        super().__init__()
        self.track_int = TrackManager(filter_type)
        self.stub = stub

    def ProcessMeasurement(self, request, context):
        track_msg = self.track_int.process_measurement(request)
        if self.stub:
          self.stub.ProcessTrack(track_msg)
        else:
          logging.warning(f"invalid stub")
        return google_dot_protobuf_dot_empty__pb2.Empty()

def serve(args):
    channel = grpc.insecure_channel("localhost:50052")
    stub = measurement_pb2_grpc.TrackProducerStub(channel)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    measurement_pb2_grpc.add_MeasurementProducerServicer_to_server(Tracker(stub, args.filter), 
                                                        server)
    server.add_insecure_port('[::]:' + str(args.recvport))
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
  args = input_args()
  serve(args)