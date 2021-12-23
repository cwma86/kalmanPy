#!/usr/bin/env python3
import argparse
import grpc
import logging
import os
import sys
import numpy as np

from concurrent import futures
from google.protobuf import text_format

script_path = os.path.dirname(os.path.abspath( __file__ ))
src_dir = os.path.dirname(script_path)
autogen_dir = os.path.join(src_dir,"auto_generated")
sys.path.insert(1, autogen_dir)
import measurement_pb2_grpc
import measurement_pb2

def input_args():
  parser = argparse.ArgumentParser(description='Run Tracker')
  parser.add_argument('-r', '--recvport',type=int, default=50051,
                    help='recieve port')
  parser.add_argument('-v', '--verbose', action='store_true',
                    help='Verbose logging')
  args = parser.parse_args()
    # initialize logger format
  logLevel = logging.INFO
  if args.verbose:
    logLevel = logging.DEBUG
  logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)-8s\
       [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logLevel)
  logging.info(f"logging set to {logging.getLevelName(logLevel)}")
  logging.debug(f"Recving data on port {args.recvport}")

  return args

class Tracker(measurement_pb2_grpc.TrackerServicer):
    meas = []
    def ProcessMeasurement(self, request, context):
        text_proto = text_format.MessageToString(request)
        output_str = text_format.Parse(text_proto, measurement_pb2.measurement())
        logging.info(f"request: {output_str}")
        self.meas.append(request)
        pred_vel = np.array([[0],[0],[0]])
        if len(self.meas) >= 2:
          dt = self.meas[-1].time - self.meas[-2].time
          finalmeas = np.array([[self.meas[-1].x],
                                [self.meas[-1].y],
                                [self.meas[-1].z],])

          initmeas = np.array([[self.meas[-2].x],
                                [self.meas[-2].y],
                                [self.meas[-2].z],])
          pred_vel = (finalmeas - initmeas) / dt
          print(f"{finalmeas} -{ initmeas} / ({dt})")
          print(f"pred_vel {pred_vel}")

        track_msg = measurement_pb2.track(x_velocity=pred_vel[0],
                                          y_velocity=pred_vel[1],
                                          z_velocity=pred_vel[2])
        for i in range(len(self.meas)):
          meas =  self.meas[i].SerializeToString()
          track_msg.measurements.append(meas)
        return track_msg

def serve(args):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    measurement_pb2_grpc.add_TrackerServicer_to_server(Tracker(), server)
    server.add_insecure_port('[::]:' + str(args.recvport))
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
  args = input_args()
  serve(args)