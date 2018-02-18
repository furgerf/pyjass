#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import math

import coloredlogs


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
