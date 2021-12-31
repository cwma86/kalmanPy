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
  """
    Input argument parser
    ...
  """
  # Parse input arguments
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
  """
    A Class used for managing simulated targets, maintianing their current 
    state, estimating true postion, and measured postion (added uncertainty)

    Attributes
    ---------
    positions: List
              a python list of simulated target measurements 
              as defined by measurement_pb2.measurement
    x_vel: float
          The simulated targets instanteous velocity in the x coordinate
    y_vel: float
          The simulated targets instanteous velocity in the y coordinate
    z_vel: float
          The simulated targets instanteous velocity in the z coordinate
    sigma: double
          The uncertainty in the measured postion for each corrdinate
          (assumes equal value for each coordinate)
    
    Methods
    -------
    predict_at_time()
      given a provided input time this method will produce a new measurement
      group containing both measured and true positions for each target being 
      being managed by the Simulator class (self.positions)
    
  """
  def __init__(self, x_init, y_init, z_init, 
                      x_vel=0, y_vel=0, z_vel=0, 
                      time=time.time()):
    # TODO this currently only implements a single simulated target
    # This should be updated to maintain multiple targets
    self.positions = [measurement_pb2.measurement(x=x_init,
                                                y=y_init,
                                                z=z_init,
                                                time=time)]
    self.x_vel = x_vel
    self.y_vel = y_vel
    self.z_vel = z_vel

    # TODO assumes equal error values in each corrdinate direction
    # It would be good to improve this to provide a more detailed uncertatiny
    # error values
    self.sigma = 0.5

  def predict_at_time(self, time) -> measurement_pb2.measurement_group:
    """
      Given a provided input time this method will produce a new measurement
      group containing both measured and true positions for each target being 
      being managed by the Simulator class (self.positions)

      Parameters
      --------
      time: float
        The time at which you wish the target to be prdicted too
        This must be in the same time frame as the simulator was initialized (e.g linux epoch)
        This assumes target velocity is is the same time frame (e.g time = seconds, velocity units/second)
    
      Returns
      ---------
        meas group: measurement_pb2.measurement_group
          returns a single measurement group containing the measuremed postions
          of each target being maintained by the simulator (self.positions) at 
          the desired time
    """
    # Predict the position forward
    new_meas_group = measurement_pb2.measurement_group()
    for i in range(len(self.positions)):
      dt = time - self.positions[i].time
      if dt < 0:
        dt = 0
      logging.debug(f"predicting measurement position {i} " +
                    f"to time {time} with a dt of {dt}")

      pos = np.array([[self.positions[i].x],
                      [self.positions[i].y],
                      [self.positions[i].z]])
      vel = np.array([[self.x_vel],
                      [self.y_vel],
                      [self.z_vel]])
      new_true_pos = pos + vel * dt    
      # add uncertainty to the new position
      new_pos = random.gauss(new_true_pos, self.sigma)

      new_meas = measurement_pb2.measurement(x=new_pos[0],
                                              y=new_pos[1],
                                              z=new_pos[2],
                                              time=time,
                                              true_x=new_true_pos[0],
                                              true_y=new_true_pos[1],
                                              true_z=new_true_pos[2])
      text_proto = text_format.MessageToString(new_meas)
      output_str = text_format.Parse(text_proto, measurement_pb2.measurement())
      logging.debug(f"output: \n {output_str}")
      new_meas_group.measurements.append(new_meas.SerializeToString())
    logging.info(f"Producing a new measurement group with " +
                 f"{len(new_meas_group.measurements)} measurements")
    return new_meas_group
    

def run(args):
  """
    Runs the simulator
  """
  starttime = time.time()
  logging.debug(f"run time {starttime}")

  # Set initial positions for the targets to be simulated
  sim = Simulator(10, 12, 13,
                  x_vel=1, y_vel=2, z_vel=0.5, 
                      time=starttime)
  while True:
    try:
      # Connect to the track consumer
      with grpc.insecure_channel(args.hostport) as channel:
        stub = measurement_pb2_grpc.MeasurementProducerStub(channel)
        # Grab the current time and predict the simulated measurement to this time
        updatetime = time.time()
        logging.debug(f"updatetiem {updatetime}")
        measurement_update = sim.predict_at_time(updatetime)
        stub.ProcessMeasurement(measurement_update)
        # repeat measurement production every 5 seconds
        time.sleep(5)
    except grpc.RpcError as rpc_error:
      # Failed to connect, retry in 5 seconds
      logging.warning(f"failed to connect {rpc_error.code()}, retry in 5 seconds")
      time.sleep(5)


if __name__ == "__main__":
  args = input_args()
  run(args)