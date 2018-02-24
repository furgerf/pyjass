#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
import time
import traceback
from argparse import ArgumentParser
from config import Config

import numpy as np

import utils
from game import Game

def parse_arguments():
  parser = ArgumentParser()
  # general
  parser.add_argument("--loglevel", type=str, nargs="?", default="INFO",
      help="Minimum log level of logged messages")
  parser.add_argument("--seed", type=int, nargs="?", const=42,
      help="Random seed to use, no seed means random")

  # files
  parser.add_argument("--store-data", action="store_true",
      help="True if trainings data should be stored")
  parser.add_argument("--training-file", default="foo",
      help="Name of the training data file to use without ending")
  parser.add_argument("--eid", required=True, help="ID of the evaluation")

  # game settings
  parser.add_argument("--online-training", action="store_true",
      help="True if any learning model should be trained while playing")
  parser.add_argument("--team1", choices=Game.PLAYER_TYPES.keys(), default="random",
      help="Strategy for team 1")
  parser.add_argument("--team1-best", action="store_true",
      help="True if team 1 should always choose the best card")
  parser.add_argument("--team2", choices=Game.PLAYER_TYPES.keys(), default="random",
      help="Strategy for team 2")
  parser.add_argument("--team2-best", action="store_true",
      help="True if team 2 should always choose the best card")

  # intervals
  parser.add_argument("--hands", type=float, nargs="?", default=1e4,
      help="Number of hands to play")
  parser.add_argument("--logint", type=float, nargs="?",
      help="Progress log interval (number of hands), defaults to hands/10")
  parser.add_argument("--trainingint", type=float, nargs="?", default=1e4,
      help="Training interval for storing data/online training (number of hands)")
  parser.add_argument("--checkpointint", type=float, nargs="?", default=1e5,
      help="Checkpoint creation interval (number of hands)")

  # apply args
  return parser.parse_args()

def main():
  start_time = time.time()
  args = parse_arguments()

  # apply args
  if args.seed:
    np.random.seed(args.seed)

  if args.store_data:
    Config.STORE_TRAINING_DATA = True
  if args.online_training:
    Config.ONLINE_TRAINING = True
  Config.TRAINING_DATA_FILE_NAME = "data/{}.csv".format(args.training_file)
  Config.EVALUATION_DIRECTORY = "evaluations/{}".format(args.eid)

  if args.team1:
    Config.TEAM_1_STRATEGY = args.team1
  if args.team1_best:
    Config.TEAM_1_BEST = args.team1_best
  if args.team2:
    Config.TEAM_2_STRATEGY = args.team2
  if args.team2_best:
    Config.TEAM_2_BEST = args.team2_best

  if args.hands:
    Config.TOTAL_HANDS = int(args.hands)
  if args.logint:
    Config.LOGGING_INTERVAL = int(args.logint)
  else:
    Config.LOGGING_INTERVAL = Config.TOTAL_HANDS / 10
  if args.trainingint:
    Config.TRAINING_INTERVAL = int(args.trainingint)
  if args.checkpointint:
    Config.CHECKPOINT_INTERVAL = int(args.checkpointint)

  # set up logging
  log = utils.get_logger("jass")
  log.info("Args: {}".format(args))
  log.debug("Config: {}".format(
    {key: utils.format_human(Config.__dict__[key]) if isinstance(Config.__dict__[key], int)
      else Config.__dict__[key] for key in filter(lambda key: not key.startswith("__"), Config.__dict__)}))
  if args.loglevel:
    log.setLevel(args.loglevel.upper())

  # config sanity checks

  # make sure the evaluation doesn't overwrite existing data
  evaluation_lock = "{}/has-eval".format(Config.EVALUATION_DIRECTORY)
  if os.path.exists(evaluation_lock):
    log.error("Aborting evaluation because directory {} already contains an evaluation!"
        .format(Config.EVALUATION_DIRECTORY))
    return
  open(evaluation_lock, "a").close() # touch eval lock

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