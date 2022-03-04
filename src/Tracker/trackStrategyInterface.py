import logging
import numpy as np
from abc import ABCMeta, abstractmethod
from google.protobuf import text_format

import measurement_pb2

class trackStrategyInterface:
  __metaclass__ = ABCMeta
  @classmethod
  def version(self): 
    return "1.0"

  @abstractmethod
  def add_measurement(self, 
                      meas: measurement_pb2.measurement): 
    raise NotImplementedError
  
  def print_meas(self, meas: measurement_pb2.measurement):
    text_proto = text_format.MessageToString(meas)
    output_str = text_format.Parse(text_proto, measurement_pb2.measurement())
    logging.info(f"meas: {output_str}")
