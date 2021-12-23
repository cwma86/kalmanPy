#!/usr/bin/env python3
import argparse
import grpc
import logging
import os
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
    format='%(asctime)s,%(msecs)d %(levelname)-8s\
       [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logLevel)
  logging.info(f"logging set to {logging.getLevelName(logLevel)}")
  logging.debug(f"Server host port: {args.hostport}")

  return args

class Simulator:
  def __init__(self, x_init, y_init, z_init, 
                      x_vel=0, y_vel=0, z_vel=0, 
                      time=time.time()):
    print(f"constructor time {time}")
    self.position = measurement_pb2.measurement(x=x_init,
                                                y=y_init,
                                                z=z_init,
                                                time=time)
    print(f"self.position.x: {self.position.x}")
    print(f"self.position.y: {self.position.y}")
    print(f"self.position.y: {self.position.time}")
    self.x_vel = x_vel
    self.y_vel = y_vel
    self.z_vel = z_vel

  def predict_at_time(self, time):
    dt = time - self.position.time
    if dt < 0:
      dt = 0
    print(f"dt: {time} - {self.position.time} = {dt}")
    x_pos = self.position.x + self.x_vel * dt
    y_pos = self.position.y + self.y_vel * dt
    z_pos = self.position.z + self.z_vel * dt
    new_meas = measurement_pb2.measurement(x=x_pos,
                                            y=y_pos,
                                            z=z_pos,
                                            time=time)
    text_proto = text_format.MessageToString(new_meas)
    output_str = text_format.Parse(text_proto, measurement_pb2.measurement())
    print(f"output: \n {output_str}")
    return new_meas
    



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
        print(f"received velocity of x: {response.x_velocity}")
        print(f"received velocity of y: {response.y_velocity}")
        print(f"received velocity of z: {response.z_velocity}")
        print(f"using : {len(response.measurements)} measurements")
        time.sleep(5)
    except grpc.RpcError as rpc_error:
      print(f"failed to connect {rpc_error.code()}, retry in 5 seconds")
      time.sleep(5)



if __name__ == "__main__":
  args = input_args()
  run(args)