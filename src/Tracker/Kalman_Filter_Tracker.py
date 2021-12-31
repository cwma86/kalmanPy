import logging
import numpy as np

import TrackInterface as ti 
import measurement_pb2

class Kalman_Filter_Tracker(ti.TrackInterface):
  """
    A class used to represent a Kalman filter

    ...

    Attributes
    ----------
    X : np matrix
        State matrix (pos/vel)
        expected in following format
        [[x]
         [y]
         [z]
         [x_dt]
         [y_dt]
         [z_dt]]
    P : np matrix
        Process (state) cov matrix Error in the estimation process
    K : float
        Kalman Gain (weight factor) based on comparing error in estimate from
        error in the measurement
    R : np matrix
        Sensor Noise cov Matrix (error in the measurement)
    I : np matrix
        Identity matrix
    u : np matrix
        control var Matrix (Acceleration)
    w : np matrix
        pred state noise matrix
    Q : np matrix
        process noise cov matrix (keeps P from going to 0)
    time : float
        Time of the current state
    Methods
    -------
    predict()
        Predicts the current stored state forward
    measurement_input()
        takes an external measurement, that can be used to update stored state
    update()
        takes a new measurement, and a state prediction and update the stored state
  """
  def __init__(self) -> None:
    self.X = None # State matrix (pos/vel)

    # TODO find better way to initialize P
    self.P = np.identity(6) * 0.5 # Process cov matrix

    # TODO figure out how to use R value
    self.R =  np.zeros((3,3)) #np.array([]) # Sensor Noise cov Matrix
    self.I = np.array([]) # identity Matrix
    self.u = np.zeros((3,1)) # control var matrix (Acceleration)

    # TODO figure out how to use w value
    self.w = np.array([[0],
                      [0],
                      [0],
                      [0],
                      [0],
                      [0]]) # np.array([]) # pred state noise matrix
    # TODO figure out how to use Q value
    self.Q = np.zeros((6,6)) # np.array([]) # process noise cov matrix
    self.time = 0 # state update time 
    self.meas_list = []


  def predict(self, time):
    """
      Predict the stored filter state forward

      ...
      Parameters
      -------
      None:
          none
      Returns
      -------
      new_X : np matrix
        The current stored state of the filter predicted forward
      new_P : np matrix
        The current stored Proc cov matrix predicted forward
    """
    dt = time - self.time
    logging.debug(f"dt: {dt}")
    A = np.identity(6)
    A[0][3] = dt
    A[1][4] = dt
    A[2][5] = dt
    B = np.array([[0.5 * dt **2, 0.0          , 0.0         ],
                  [0.0         , 0.5 * dt **2 , 0.0         ],
                  [0.0         , 0.0          , 0.5 * dt **2],
                  [dt          , 0            , 0           ],
                  [0.0         , dt           , 0           ],
                  [0.0         , 0            , dt          ]])

    new_x = A @ self.X + B @ self.u + self.w
    logging.debug(f"new measurement prediction: \n{new_x}")
    new_P = A @ self.P @ A.T + self.Q
    logging.debug(f"A: \n{A}")
    logging.debug(f"old P: \n{self.P}")
    logging.debug(f"new P: \n{new_P}")

    return new_x, new_P

  def measurement_input(self, X, time, z):
    """
      Take a measurement input, add measurement noise, predict
      The current state forward, and update the current state

      ...
      Parameters
      -------
      X: np matrix
          new input measurement
          format:
          [[x],
           [y],
           [z]]
      z: np matrix
          measurement noise (uncertainty)
      Returns
      -------
      None: 
          none
    """
    C = np.identity(3)
    Y = C @ X + z
    logging.debug(f"new measured value: {Y}")
    new_X, new_P = self.predict(time)
    self.update(new_X, new_P, time, Y)

  def update(self, new_X, new_P, time, Y):
    """
      Update the current filter state

      ...
      Parameters
      -------
      new_X: np matrix
          Current state predicted forward to new measurement time
      new_P: np matrix
          Current Process cov predicted forward to new measurement time
      Y: np matrix
          New measurement to be used for updating current state
      Returns
      -------
      None: 
          none
    """
    H = np.zeros((3,6))
    H[0][0] = 1
    H[1][1] = 1
    H[2][2] = 1
    H[0][3] = 1
    H[1][4] = 1
    H[2][5] = 1
    s = H @ new_P @ H.T + self.R
    K =  new_P @ H.T @ np.linalg.inv(s) # Kalman gain
    self.X = new_X + K @ (Y - H @ new_X)
    logging.debug(f"Updating filter X: \n {self.X}")

    self.P = new_P
    logging.debug(f"Updating filter P: \n {self.P}")

    self.time = time
    logging.debug(f"Updating filter time: \n {self.time}")



  def add_measurement(self, 
                      meas: measurement_pb2.measurement) -> measurement_pb2.track:
    X = np.array([[meas.x],
                  [meas.y],
                  [meas.z]])
    if self.X is None:
      self.X = np.array([[meas.x],
                         [meas.y],
                         [meas.z],
                         [0],
                         [0],
                         [0]])
      self.time = meas.time
    else:
      self.measurement_input( X, meas.time, z=1.0)
    self.meas_list.append(meas)
    track_msg = measurement_pb2.track(x_velocity=self.X[3],
                                      y_velocity=self.X[4],
                                      z_velocity=self.X[5])
    for i in range(len(self.meas_list)):
      measurement =  self.meas_list[i].SerializeToString()
      track_msg.measurements.append(measurement)
    return track_msg

