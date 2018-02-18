#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import time
import traceback
from config import Config

import numpy as np

import utils
from game import Game

if __name__ == "__main__":
  if not Config.RANDOM:
    np.random.seed(42)

  game = None
  start_time = time.time()
  log = utils.get_logger("jass")
  log.setLevel(Config.LOG_LEVEL)

  try:
    game = Game(log)
    game.play()
  except Exception as ex:
    log.critical("{} during evaluation: {}".format(type(ex).__name__, str(ex)))
    log.critical(traceback.format_exc())
    sys.exit(1)
  finally:
    mins, secs = divmod(time.time() - start_time, 60)
    hours, mins = divmod(mins, 60)
    time_string = \
        "{}h{}m{:.1f}s".format(int(hours), int(mins), secs) if hours > 0 else \
        "{}m{:.1f}s".format(int(mins), secs) if mins > 0 else \
        "{:.1f}s".format(secs)
    log.warning("Finished execution after {}".format(time_string))
    logging.shutdown()

