#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import csv
import logging
import math
import struct
from itertools import chain, islice

import numpy as np

import coloredlogs
from const import Const


def get_logger(name):
  """
  debug_levelv_num = 21
  # add "success" log level
  logging.addLevelName(debug_levelv_num, "SUCCESS")
  def success(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(debug_levelv_num):
      self._log(debug_levelv_num, message, args, **kws)
  logging.Logger.success = success
  """

  # set up logger
  coloredlogs.install(level="DEBUG")
  coloredlogs.DEFAULT_LEVEL_STYLES = {
      "debug": {"color": "white", "bold": False},
      "info": {"color": "white", "bold": True},
      "success": {"color": "green", "bold": True},
      "warning": {"color": "yellow", "bold": True},
      "error": {"color": "red", "bold": True},
      "fatal": {"color": "magenta", "bold": True},
      }
  logger = logging.getLogger(name)
  handler = logging.StreamHandler()
  log_format = "%(asctime)s %(module)s.%(funcName)s:%(lineno)d %(levelname)-8s %(message)s"
  formatter = coloredlogs.ColoredFormatter(log_format)
  handler.setFormatter(formatter)
  logger.propagate = False
  logger.handlers = []
  logger.addHandler(handler)
  logger.setLevel(logging.DEBUG)
  return logger

def process_binary_file(file_name, batch_size):
  with open(file_name, "rb") as fh:
    old_position = 0
    chunk = fh.read(Const.BYTES_PER_SAMPLE * batch_size)
    while chunk:
      read_bytes = fh.tell() - old_position
      old_position = fh.tell()
      data = np.array([np.array(struct.unpack("={}h".format(Const.CARDS_PER_HAND * "B"),
          chunk[i*Const.BYTES_PER_SAMPLE:(i+1)*Const.BYTES_PER_SAMPLE]), dtype=int)
          for i in range(int(read_bytes / Const.BYTES_PER_SAMPLE))])
      yield data
      chunk = fh.read(Const.BYTES_PER_SAMPLE * batch_size)

def process_csv_file(file_name):
  with open(file_name, "r") as fh:
    for row in csv.reader(fh):
      yield row

def batch(iterator, batch_size):
  while True:
    batched_iterator = islice(iterator, batch_size)
    # pylint: disable=stop-iteration-return
    yield chain([next(batched_iterator)], batched_iterator)

def format_cards(cards):
  return " ".join(str(c) for c in cards)

def format_human(number):
  unit = 1000
  if number < unit:
    return str(number)
  magnitude = int(math.log(number) / math.log(unit))
  pre = "kMGTPE"[magnitude-1]
  scaled_number = number / math.pow(unit, magnitude)
  if scaled_number == int(scaled_number):
    scaled_number = int(scaled_number)
  return "{}{}".format(scaled_number, pre)

class StoreDictKeyPair(argparse.Action):
  def __call__(self, parser, namespace, values, option_string=None):
    my_dict = {}
    for kv in values.split(";"):
      key, val = kv.split("=")
      my_dict[key] = eval(val) # pylint: disable=eval-used
    setattr(namespace, self.dest, my_dict)
