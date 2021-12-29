#!/usr/bin/env python3
import argparse
import grpc
import logging
import numpy as np
import os
import random
import sys
import time

from google.protobuf import text_format

script_path = os.path.dirname(os.path.abspath( __file__ ))
src_dir = os.path.dirname(script_path)
autogen_dir = os.path.join(src_dir,"auto_generated")
sys.path.insert(1, autogen_dir)
import measurement_pb2_grpc
import measurement_pb2

def input_args():
  parser = argparse.ArgumentParser(description='Run Tracker')
  parser.add_argument('-s', '--hostport', default='localhost:50051',
                    help='server host port')
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
  logging.debug(f"Server host port: {args.hostport}")

  return args

class Simulator:
  def __init__(self, x_init, y_init, z_init, 
                      x_vel=0, y_vel=0, z_vel=0, 
                      time=time.time()):
    self.positions = [measurement_pb2.measurement(x=x_init,
                                                y=y_init,
                                                z=z_init,
                                                time=time)]
    self.x_vel = x_vel
    self.y_vel = y_vel
    self.z_vel = z_vel
    # error values
    self.sigma = 0.5

  def predict_at_time(self, time) -> measurement_pb2.measurement_group:
    # Predict the position forward
    new_meas_group = measurement_pb2.measurement_group()
    for i in range(len(self.positions)):
      dt = time - self.positions[i].time
      if dt < 0:
        dt = 0

      pos = np.array([[self.positions[i].x],
                      [self.positions[i].y],
                      [self.positions[i].z]])
      vel = np.array([[self.x_vel],
                      [self.y_vel],
                      [self.z_vel]])
      new_pos = pos + vel * dt    
      # add uncertainty to the new position
      new_pos = random.gauss(new_pos, self.sigma)

      new_meas = measurement_pb2.measurement(x=new_pos[0],
                                              y=new_pos[1],
                                              z=new_pos[2],
                                              time=time)
      text_proto = text_format.MessageToString(new_meas)
      output_str = text_format.Parse(text_proto, measurement_pb2.measurement())
      print(f"output: \n {output_str}")
      new_meas_group.measurements.append(new_meas.SerializeToString())
    return new_meas_group
    

def run(args):
  starttime = time.time()
  print(f"run time {starttime}")
  sim = Simulator(1, 2, 3,
                  x_vel=1, y_vel=2, z_vel=0.5, 
                      time=starttime)
  while True:
    try:
      with grpc.insecure_channel(args.hostport) as channel:
        stub = measurement_pb2_grpc.TrackerStub(channel)
        updatetime = time.time()
        measurement_update = sim.predict_at_time(updatetime)
        response = stub.ProcessMeasurement(measurement_update)
        for i in range(len(response.tracks)):
          track = measurement_pb2.track()
          track.ParseFromString(response.tracks[i])

          print(f"received velocity of x: {track.x_velocity}")
          print(f"received velocity of y: {track.y_velocity}")
          print(f"received velocity of z: {track.z_velocity}")
          print(f"using : {len(track.measurements)} measurements")
        time.sleep(5)
    except grpc.RpcError as rpc_error:
      print(f"failed to connect {rpc_error.code()}, retry in 5 seconds")
      time.sleep(5)



if __name__ == "__main__":
  args = input_args()
  run(args)