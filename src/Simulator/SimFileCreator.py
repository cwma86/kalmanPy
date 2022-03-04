#!/usr/bin/env python3
import argparse
import logging
import numpy as np
import os
import sys

script_path = os.path.dirname(os.path.abspath( __file__ ))
src_dir = os.path.dirname(script_path)
sim_dir = os.path.join(src_dir,"Simulator")
sys.path.insert(1, sim_dir)
from simulator import Simulator
from simulator import initialize_track_creation

autogen_dir = os.path.join(src_dir,"auto_generated")
sys.path.insert(1, autogen_dir)
import measurement_pb2

def input_args():
  """
    Input argument parser
    ...
  """
  # Parse input arguments
  parser = argparse.ArgumentParser(description='Run Tracker')
  parser.add_argument('-f', '--filepath', default="track",
                    help='file base name')
  parser.add_argument('-v', '--verbose', action='store_true',
                    help='Verbose logging')
  parser.add_argument('-t', '--time', default=120, type=int,
                    help='Length of the scenario in seconds (default:120)')
  parser.add_argument('-n', '--numtrack', default=1, type=int,
                    help='number of tracks to create')
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

  return args

def run(args):
  """
    Runs the simulator
  """
  for i in range(args.numtrack):
    run_time = 0
    init_x, init_y, init_z, velx, vely, velz, accx, accy, accz = initialize_track_creation()
    sim = Simulator(init_x, init_y, init_z,
                    x_vel=velx, y_vel=vely, z_vel=velz, 
                    x_acc=accx, y_acc=accy, z_acc=accz, 
                        time=run_time)
    f = None
    if (args.filepath):
      f = open(args.filepath+str(i)+".csv", 'w')
      f.write("# Measurement time, meas_x, meas_y, meas_z, true_x, true_y, true_z, true_velx, true_vely, true_velz, true_accx, true_accy, true_accz\n")

    while run_time < args.time:
      # Grab the current time and predict the simulated measurement to this time
      updatetime = round(run_time)
      logging.debug(f"updatetiem {updatetime}")
      measurement_update = sim.predict_at_time(updatetime)
      for i in range(len(measurement_update.measurements)):
        measurement = measurement_pb2.measurement()
        measurement.ParseFromString(measurement_update.measurements[i])
        print(f"measurements{ measurement.time}")
        if f:
          f.write(f"{measurement.time},{measurement.x},{measurement.y},{measurement.z},"
                  f"{measurement.true_x},{measurement.true_y},{measurement.true_z},"
                  f"{velx},{vely},{velz},"
                  f"{accx},{accy},{accz}\n")
      # repeat measurement production every 5 seconds
      run_time = run_time + 2
    if f:
      f.close()


if __name__ == "__main__":
  args = input_args()
  run(args)