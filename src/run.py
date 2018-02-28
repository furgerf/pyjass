#seli!/usr/bin/env python
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
from encoding import Encoding

def parse_arguments():
  parser = ArgumentParser()

  # general
  parser.add_argument("--loglevel", type=str, nargs="?", default="INFO",
      help="Minimum log level of logged messages, defaults to INFO")
  parser.add_argument("--seed", type=int, nargs="?", const=42,
      help="Random seed to use, no seed means random")
  parser.add_argument("--seed2", type=int, nargs="?", const=123,
      help="Alternative random seed to use, no seed means random")

  # files
  parser.add_argument("--store-data", action="store_true",
      help="True if trainings data should be stored")
  parser.add_argument("--training-file",
      help="Name of the training data file to use, overriding the default file")
  parser.add_argument("--model", required=True,
      help="Name of the folder in the models/ directory, determines the encoding to use")
  parser.add_argument("--regressor-name",
      help="Name of the regressor file in the model directory to use instead of the default, for all learners")
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
  default_hands = 1e4
  parser.add_argument("--hands", type=float, nargs="?", default=default_hands,
      help="Number of hands to play, defaults to {}".format(default_hands))
  parser.add_argument("--logint", type=float, nargs="?",
      help="Progress log interval (number of hands), defaults to hands/50")
  parser.add_argument("--trainingint", type=float, nargs="?", # NOTE: 1e5 is roughly 1.25 GB RAM
      help="Training interval for storing data/online training (number of hands), defaults to min(hands/10, 1e5)")
  parser.add_argument("--chkint", type=float, nargs="?",
      help="Checkpoint creation interval (number of hands), defaults to hands/10")
  parser.add_argument("--chkresolution", type=float, nargs="?",
      help="Checkpoint data resolution (number of hands), defaults to checkpoint interval/10")

  return parser.parse_args()

def apply_arguments(args):
  # pylint: disable=too-many-branches
  if args.seed:
    np.random.seed(args.seed)
  if args.seed2:
    np.random.seed(args.seed2)

  if args.store_data:
    Config.STORE_TRAINING_DATA = True
  if args.online_training:
    Config.ONLINE_TRAINING = True
  if args.model:
    Config.MODEL_DIRECTORY = "models/{}".format(args.model)
    Config.ENCODING = get_encodings().get(args.model)
  if args.regressor_name:
    Config.REGRESSOR_NAME = args.regressor_name
  if args.training_file:
    Config.TRAINING_DATA_FILE_NAME = "data/{}".format(args.training_file)
  else:
    Config.TRAINING_DATA_FILE_NAME = "data/{}".format(Config.ENCODING.training_data_file_name)
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
    Config.LOGGING_INTERVAL = Config.TOTAL_HANDS / 50
  if args.trainingint:
    Config.TRAINING_INTERVAL = int(args.trainingint)
  else:
    Config.TRAINING_INTERVAL = min(Config.TOTAL_HANDS / 10, int(1e5))
  if args.chkint:
    Config.CHECKPOINT_INTERVAL = int(args.chkint)
  else:
    Config.CHECKPOINT_INTERVAL = Config.TOTAL_HANDS / 10
  if args.chkresolution:
    Config.CHECKPOINT_RESOLUTION = int(args.chkresolution)
  else:
    Config.CHECKPOINT_RESOLUTION = Config.CHECKPOINT_INTERVAL / 10

def check_config(log):
  # pylint: disable=too-many-return-statements
  model_based_strategies = ["sgd", "mlp"]
  uses_model = Config.TEAM_1_STRATEGY in model_based_strategies or \
      Config.TEAM_2_STRATEGY in model_based_strategies

  if not Config.MODEL_DIRECTORY or not Config.ENCODING:
    log.error("Must specify an existing model/encoding")
    return False

  if uses_model:
    if not os.path.exists(Config.MODEL_DIRECTORY):
      log.error("Model directory doesn't exist")
      return False
  elif Config.ONLINE_TRAINING:
    log.error("Cannot train online when not using models")
    return False

  if Config.STORE_TRAINING_DATA:
    if not Config.TRAINING_DATA_FILE_NAME:
      log.error("Need a training file name when storing data")
      return False
    if os.path.exists(Config.TRAINING_DATA_FILE_NAME):
      log.error("Training data file exists already")
      return False

  return True

def get_encodings():
  # MD5: -
  # encoding_1 = Encoding([1, 2, 3, 4], 6, 5, 7, 1, 0, None)
  # MD5: b56c5815f61b0701e2cdd9735f9b090e  encoding-2.csv.gz
  encoding_2 = Encoding([1, 2, 3, 4], 6, 5, 7, 2, 1, "encoding-2.csv")
  # MD5: eeb9451058585f9cccfccccf2fcd16c6  encoding-3.csv.gz
  encoding_3 = Encoding([1, 2, 3, 4], 10, 20, 30, 2, 1, "encoding-3.csv")
  # MD5: de35cdc99926a01413671f0b5798b9f0  encoding-4.csv.gz
  encoding_4 = Encoding([1, 2, 3, 4], 10, 20, 30, 1, 1, "encoding-4-small.csv")
  # MD5: TBC
  encoding_5 = Encoding([10, 20, 30, 40], 1000, 4000, 16000, 1, 1, "encoding-5.csv")

  return {
      # "01": encoding_1,
      # "02": encoding_1,
      # "03": encoding_2,
      # "04": encoding_2,
      "05": encoding_2,
      "06": encoding_3,
      "07": encoding_4,
      "08": encoding_5,
      "custom": encoding_3,
      }

def main():
  start_time = time.time()
  args = parse_arguments()
  apply_arguments(args)

  # set up logging
  log = utils.get_logger("jass")
  log.info("Args: {}".format(args))
  log.debug("Config: {}".format(
    {key: utils.format_human(Config.__dict__[key]) if isinstance(Config.__dict__[key], (int, float))
      else str(Config.__dict__[key]) for key in filter(lambda key: not key.startswith("__"), Config.__dict__)}))
  if args.loglevel:
    log.setLevel(args.loglevel.upper())

  if not check_config(log):
    log.error("Aborting evaluation because config is invalid")
    return

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
    log.warning("Finished evaluation '{}' after {}".format(args.eid, time_string))
    logging.shutdown()

if __name__ == "__main__":
  main()
