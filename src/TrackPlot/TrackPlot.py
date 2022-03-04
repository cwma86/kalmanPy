#!/usr/bin/env python3
import argparse
import logging
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

def input_args():
  parser = argparse.ArgumentParser(description='Track file plotting tool')
  parser.add_argument('-f', '--filePath', type=str, required=True,
                    help='track file path')
  parser.add_argument('-v', '--verbose', action='store_true',
                    help='Verbose logging')
  args = parser.parse_args()
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


def main(args):
  if not os.path.isfile(args.filePath):
    logging.error("invalid file path")
    sys.exit(1)
  
  # Read the track file and capture track state updates and true measurment locations
  track = {"x":[], "y":[], "z":[]}
  true = {"x":[], "y":[], "z":[]}
  temp_true = {"x":None, "y":None, "z":None}
  with open(args.filePath) as f:
    for line in f:
      line = line.split()
      if line[0] == "trk":
        if temp_true['x']:
          # Store the last measurement (most recent)
          true["x"].append(temp_true["x"])
          true["y"].append(temp_true["y"])
          true["z"].append(temp_true["z"])
        # Store the track state update
        track["x"].append(float(line[1]))
        track["y"].append(float(line[2]))
        track["z"].append(float(line[3]))
      elif line[0] == "meas":
        temp_true["x"] = float(line[1])
        temp_true["y"] = float(line[2])
        temp_true["z"] = float(line[3])
    # Store the very last measurement for the final track
    if temp_true['x']:
        true["x"].append(temp_true["x"])
        true["y"].append(temp_true["y"])
        true["z"].append(temp_true["z"])
    fig = plt.figure()
    
    # syntax for 3-D projection
    ax = plt.axes(projection ='3d')
    
    # defining all 3 axes
    x = np.array(track["x"])
    y = np.array(track["y"])
    z = np.array(track["z"])
    
    # plotting
    ax.plot3D(x, y, z, 'red', label='track prediction')
    # defining all 3 axes
    x = np.array(true["x"])
    y = np.array(true["y"])
    z = np.array(true["z"])
    
    # plotting
    ax.scatter3D(x, y, z, 'green',label='true measurement')
    ax.legend()
    ax.set_title('Track and measurement plot')
    plt.show()

if __name__ == "__main__":
  args = input_args()
  main(args)