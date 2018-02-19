#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import time
import traceback
from argparse import ArgumentParser
from config import Config

import numpy as np

import utils
from game import Game


def main():
  start_time = time.time()

  parser = ArgumentParser()
  parser.add_argument("--loglevel", type=str, nargs="?", default="INFO",
      help="Minimum log level of logged messages")
  parser.add_argument("--seed", type=int, nargs="?", const=42,
      help="Random seed to use, no seed means random")

  parser.add_argument("--store-data", action="store_true",
      help="True if trainings data should be stored")

  parser.add_argument("--team1", choices=Game.PLAYER_TYPES.keys(), default="random",
      help="Strategy for team 1")
  parser.add_argument("--team2", choices=Game.PLAYER_TYPES.keys(), default="random",
      help="Strategy for team 2")

  parser.add_argument("--hands", type=int, nargs="?", default=int(1e5),
      help="Number of hands to play")
  parser.add_argument("--logint", type=int, nargs="?", default=int(1e4),
      help="Progress log interval")
  parser.add_argument("--storetrainingint", type=int, nargs="?", default=int(5e4),
      help="Store training data interval")

  # apply args
  args = parser.parse_args()
  if args.seed:
    np.random.seed(args.seed)
  if args.store_data:
    Config.STORE_TRAINING_DATA = True

  if args.team1:
    Config.TEAM_1_STRATEGY = args.team1
  if args.team2:
    Config.TEAM_2_STRATEGY = args.team2

  if args.hands:
    Config.TOTAL_HANDS = args.hands
  if args.logint:
    Config.LOGGING_INTERVAL = args.logint
  if args.storetrainingint:
    Config.STORE_TRAINING_INTERVAL = args.storetrainingint

  log = utils.get_logger("jass")
  log.info("Args: {}".format(args))
  log.debug("Config: {}".format(
    {key: Config.__dict__[key] for key in filter(lambda key: not key.startswith("__"), Config.__dict__)}))
  if args.loglevel:
    log.setLevel(args.loglevel.upper())

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

if __name__ == "__main__":
  main()
