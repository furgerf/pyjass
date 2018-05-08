#seli!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
import time
import traceback
from argparse import ArgumentParser
from config import Config
from multiprocessing import Pool

import numpy as np

import utils
from encoding import Encoding
from game import Game
from parallel_game import ParallelGame


def parse_arguments():
  parser = ArgumentParser()

  # general
  parser.add_argument("--test", action="store_true",
      help="True if nothing should be done (for testing the args)")
  parser.add_argument("--loglevel", type=str, nargs="?", default="INFO",
      help="Minimum log level of logged messages, defaults to INFO")
  parser.add_argument("--seed", type=int, nargs="?", const=42,
      help="Random seed to use, no seed means random")
  parser.add_argument("--seed2", type=int, nargs="?", const=123,
      help="Alternative random seed to use, no seed means random")
  parser.add_argument("--procs", type=int, nargs="?", default=1, const=2,
      help="Number of processes to use, defaults to 1 and sets to 2 if specified without value")
  parser.add_argument("--store-scores", action="store_true",
      help="True if game scores should be stored")

  # files
  parser.add_argument("--store-data", action="store_true",
      help="True if trainings data should be stored")
  parser.add_argument("--load-training-file",
      help="Name of the training data file to train on")
  parser.add_argument("--store-training-file",
      help="Name of the training data file to write to")
  parser.add_argument("--model", required=True,
      help="Name of the folder in the models/ directory, determines the encoding to use")
  parser.add_argument("--regressor-name",
      help="Name of the regressor file in the model directory to use instead of the default, for all learners")
  parser.add_argument("--other-regressor-name",
      help="Name of the regressor file in the model directory to use instead of the default, for 'other' learners")
  parser.add_argument("--eid", required=True, help="ID of the evaluation")

  # game settings
  parser.add_argument("--online-training", action="store_true",
      help="True if any learning model should be trained while playing")
  parser.add_argument("--team1", choices=Game.PLAYER_TYPES.keys(), default="simple",
      help="Strategy for team 1")
  parser.add_argument("--team1-best", action="store_true",
      help="True if team 1 should always choose the best card")
  parser.add_argument("--team1-args", action=utils.StoreDictKeyPair, metavar="KEY1=VAL1;KEY2=VAL2;...",
      help="Arguments for the model constructor for team 1")
  parser.add_argument("--team2", choices=Game.PLAYER_TYPES.keys(), default="simple",
      help="Strategy for team 2")
  parser.add_argument("--team2-best", action="store_true",
      help="True if team 2 should always choose the best card")

  # intervals
  default_hands = 1e4
  parser.add_argument("--hands", type=float, nargs="?", default=default_hands,
      help="Number of hands to play, defaults to {}".format(default_hands))
  # NOTE: 1e5 with 2 processes needs about 1GB of RAM which roughly doubles during training
  parser.add_argument("--trainingint", type=float, nargs="?",
      help="Training interval for storing data/online training (hands), defaults to min(hands/10, 1e5)")
  parser.add_argument("--chkint", type=float, nargs="?",
      help="Checkpoint creation interval (hands), defaults to training interval if training online, else hands/10")
  parser.add_argument("--chkresolution", type=float, nargs="?",
      help="Checkpoint data resolution (hands), defaults to checkpoint interval/10")
  parser.add_argument("--batchsize", type=float, nargs="?",
      help="Size of a single batch to run on a process, defaults to 1e3")
  parser.add_argument("--logint", type=float, nargs="?",
      help="Logging interval, defaults to hands/20")

  return parser.parse_args()

def apply_arguments(args):
  # pylint: disable=too-many-branches,too-many-statements
  if args.seed:
    Config.SEED = args.seed
  if args.seed2:
    Config.SEED = args.seed2
  if Config.SEED:
    np.random.seed(Config.SEED)
  Config.PARALLEL_PROCESSES = args.procs

  if args.store_data:
    Config.STORE_TRAINING_DATA = True
  if args.store_scores:
    Config.STORE_SCORES = True
  if args.online_training:
    Config.ONLINE_TRAINING = True
  if args.model:
    Config.MODEL_DIRECTORY = "models/{}".format(args.model)
    Config.ENCODING = get_encodings().get(args.model)
  if args.regressor_name:
    Config.REGRESSOR_NAME = args.regressor_name
  if args.other_regressor_name:
    Config.OTHER_REGRESSOR_NAME = args.other_regressor_name
  if args.load_training_file:
    Config.LOAD_TRAINING_DATA_FILE_NAME = "data/{}".format(args.load_training_file)
  if args.store_training_file:
    Config.STORE_TRAINING_DATA_FILE_NAME = "data/{}".format(args.store_training_file)
  Config.EVALUATION_DIRECTORY = "evaluations/{}".format(args.eid)
  Config.LOSS_FILE = "{}/loss.csv".format(Config.EVALUATION_DIRECTORY)

  if args.team1:
    Config.TEAM_1_STRATEGY = args.team1
  if args.team1_best:
    Config.TEAM_1_BEST = args.team1_best
  if args.team1_args:
    Config.TEAM_1_MODEL_ARGS = args.team1_args
  if args.team2:
    Config.TEAM_2_STRATEGY = args.team2
  if args.team2_best:
    Config.TEAM_2_BEST = args.team2_best

  if args.hands is not None:
    Config.TOTAL_HANDS = int(args.hands)
  if args.batchsize:
    Config.BATCH_SIZE = int(args.batchsize)
  else:
    Config.BATCH_SIZE = int(1e3)
  if args.trainingint:
    Config.TRAINING_INTERVAL = int(args.trainingint)
  else:
    Config.TRAINING_INTERVAL = min(int(Config.TOTAL_HANDS / 10), int(1e5))
  Config.TRAINING_INTERVAL = min(Config.TRAINING_INTERVAL, Config.TOTAL_HANDS)
  if args.chkint:
    Config.CHECKPOINT_INTERVAL = int(args.chkint)
  else:
    Config.CHECKPOINT_INTERVAL = Config.TRAINING_INTERVAL if Config.ONLINE_TRAINING else Config.TOTAL_HANDS / 10
  Config.CHECKPOINT_INTERVAL = min(Config.CHECKPOINT_INTERVAL, Config.TOTAL_HANDS)
  if args.chkresolution:
    Config.CHECKPOINT_RESOLUTION = int(args.chkresolution)
  else:
    Config.CHECKPOINT_RESOLUTION = min(Config.CHECKPOINT_INTERVAL / 10, Config.BATCH_SIZE)
  if args.logint:
    Config.LOGGING_INTERVAL = int(args.logint)
  else:
    Config.LOGGING_INTERVAL = int(Config.TOTAL_HANDS / 20)

  Config.set_batch_count()

def check_config(log):
  # pylint: disable=too-many-return-statements,too-many-branches
  model_based_strategies = ["sgd", "mlp", "mlp-other"]
  other_models = ["mlp-other"]
  uses_model = Config.TEAM_1_STRATEGY in model_based_strategies or \
      Config.TEAM_2_STRATEGY in model_based_strategies

  if not Config.MODEL_DIRECTORY or not Config.ENCODING:
    log.error("Must specify an existing model/encoding")
    return False

  if uses_model:
    if not os.path.exists(Config.MODEL_DIRECTORY):
      log.error("Model directory doesn't exist")
      return False
    if not Config.REGRESSOR_NAME:
      log.error("No regressor name provided")
      return False
  elif Config.ONLINE_TRAINING:
    log.error("Cannot train online when not using models")
    return False

  if (Config.TEAM_1_STRATEGY in other_models or Config.TEAM_2_STRATEGY in other_models) and \
      not Config.OTHER_REGRESSOR_NAME:
    log.error("No other regressor name provided")
    return False

  if Config.STORE_TRAINING_DATA:
    if not Config.STORE_TRAINING_DATA_FILE_NAME:
      log.error("Need a training file name when storing data")
      return False
    if os.path.exists(Config.STORE_TRAINING_DATA_FILE_NAME) and \
        os.stat(Config.STORE_TRAINING_DATA_FILE_NAME).st_size > 0:
      log.error("Training data file exists already")
      return False

  if Config.LOAD_TRAINING_DATA_FILE_NAME and not os.path.exists(Config.LOAD_TRAINING_DATA_FILE_NAME):
    log.error("Training data file to load doesn't exist!")
    return False

  actually_plays_hands = Config.TOTAL_HANDS > 0

  if actually_plays_hands and Config.TOTAL_HANDS % Config.CHECKPOINT_INTERVAL != 0:
    log.error("Checkpoint interval {} must divide total hands {}".format(
      utils.format_human(Config.CHECKPOINT_INTERVAL), utils.format_human(Config.TOTAL_HANDS)))
    return False

  if Config.LOGGING_INTERVAL % (Config.BATCH_SIZE*Config.PARALLEL_PROCESSES) != 0:
    log.error("Batch size {} times processes {} must divide logging interval {}".format(
      utils.format_human(Config.BATCH_SIZE), Config.PARALLEL_PROCESSES, utils.format_human(Config.LOGGING_INTERVAL)))
    return False

  if Config.CHECKPOINT_INTERVAL % (Config.BATCH_SIZE*Config.PARALLEL_PROCESSES) != 0:
    log.error("Batch size {} times processes {} must divide checkpoint interval {}".format(
      utils.format_human(Config.BATCH_SIZE), Config.PARALLEL_PROCESSES, utils.format_human(Config.CHECKPOINT_INTERVAL)))
    return False

  if (Config.STORE_TRAINING_DATA or Config.ONLINE_TRAINING) and actually_plays_hands and \
      Config.TOTAL_HANDS % Config.TRAINING_INTERVAL != 0:
    log.error("Training interval {} must divide total hands {}".format(
      utils.format_human(Config.TRAINING_INTERVAL), utils.format_human(Config.TOTAL_HANDS)))
    return False

  if (Config.STORE_TRAINING_DATA or Config.ONLINE_TRAINING) and \
      Config.TRAINING_INTERVAL % (Config.BATCH_SIZE*Config.PARALLEL_PROCESSES) != 0:
    log.error("Batch size {} times processes {} must divide training interval {}".format(
      utils.format_human(Config.BATCH_SIZE), Config.PARALLEL_PROCESSES, utils.format_human(Config.TRAINING_INTERVAL)))
    return False

  if Config.ONLINE_TRAINING and Config.CHECKPOINT_INTERVAL < Config.TRAINING_INTERVAL:
    log.error("Checkpoint interval {} should be greater than training interval {}".format(
      utils.format_human(Config.CHECKPOINT_INTERVAL), utils.format_human(Config.TRAINING_INTERVAL)))
    return False

  if Config.STORE_SCORES and (Config.STORE_TRAINING_DATA or Config.ONLINE_TRAINING) and actually_plays_hands and \
      (Config.TRAINING_INTERVAL%Config.CHECKPOINT_INTERVAL) * (Config.CHECKPOINT_INTERVAL%Config.TRAINING_INTERVAL):
    log.error("Training interval {} must be a multiple of checkpoint interval {} or vice versa".format(
      utils.format_human(Config.TRAINING_INTERVAL), utils.format_human(Config.CHECKPOINT_INTERVAL)))
    return False

  if Config.STORE_SCORES and (Config.BATCH_SIZE % Config.CHECKPOINT_RESOLUTION) != 0:
    log.error("The checkpoint resolution {} must divide the batch size {}".format(
      utils.format_human(Config.CHECKPOINT_RESOLUTION), Config.BATCH_SIZE))
    return False

  if (Config.TOTAL_HANDS % (Config.BATCH_SIZE * Config.PARALLEL_PROCESSES)) != 0 or \
      Config.BATCH_COUNT * Config.BATCH_SIZE * Config.PARALLEL_PROCESSES != Config.TOTAL_HANDS:
    log.error("The configuration would lead to incomplete batches: {} hands can't be split into parts of {}*{}={}"
        .format(utils.format_human(Config.TOTAL_HANDS), utils.format_human(Config.PARALLEL_PROCESSES),
          utils.format_human(Config.BATCH_SIZE), utils.format_human(Config.PARALLEL_PROCESSES*Config.BATCH_SIZE)))
    return False

  return True

def get_encodings():
  # NOTE: Retired
  encoding_1 = Encoding("random", [1, 2, 3, 4], 6, 5, 7, 1, 0)

  # NOTE: Retired - bad encoding for in hand/in play/selected
  encoding_2 = Encoding("random", [1, 2, 3, 4], 6, 5, 7, 1, 1)

  # NOTE: Retired - changed card encoding
  encoding_3 = Encoding("random", [1, 2, 3, 4], 10, 20, 30, 1, 1)

  # NOTE: Retired - should've had different cost but there was a bug...
  encoding_4 = Encoding("random", [1, 2, 3, 4], 10, 20, 30, 1, 1)

  # NOTE: Retired - same encoding as 3 but data from simple
  encoding_5 = Encoding("simple", [1, 2, 3, 4], 10, 20, 30, 1, 1)

  # NOTE: Retired - same encoding as 4 but data from simple
  encoding_6 = Encoding("simple", [1, 2, 3, 4], 10, 20, 30, 1, 1)

  # NOTE: NOT EXPLORED -  changed card encoding
  encoding_7 = Encoding("simple", [10, 20, 30, 40], 1000, 4000, 16000, 1, 1)

  # NOTE: Retired- changed cost
  encoding_8 = Encoding("simple", [1, 2, 3, 4], 10, 20, 30, 4, 1)

  # NOTE: Retired- changed cost
  encoding_9 = Encoding("simple", [1, 2, 3, 4], 10, 20, 30, 2, 1)

  # NOTE: Retired- changed cost
  encoding_10 = Encoding("simple", [1, 2, 3, 4], 10, 20, 30, 1, 2)

  # NOTE: Retired - tried relative player encoding but src had a bug...
  encoding_11 = Encoding("simple", [1, 2, 3, 4], 10, 20, 30, 1, 2)

  # NOTE: Retired - using relative player encoding
  encoding_12 = Encoding("simple", [1, 2, 3, 4], 10, 20, 30, 1, 2, True)

  # NOTE: Retired - using better baseline
  encoding_13 = Encoding("better", [1, 2, 3, 4], 10, 20, 30, 1, 2, True)

  # NOTE: Retired - using relative in-play encoding
  encoding_14 = Encoding("better", [1, 2, 3, 4], 10, [44, 33, 22], 100, 1, 2, True, True)

  # NOTE: Currently explored - highlighting team-mate
  encoding_15 = Encoding("better", [1, 2, 13, 4], 50, [125, 200, 100], 250, 1, 2, True, True)

  # NOTE: Currently explored - changed cost back to how it was earlier
  encoding_16 = Encoding("better", [1, 2, 13, 4], 50, [125, 200, 100], 250, 2, 1, True, True)

  return {
      "01": encoding_1,
      "02": encoding_1,
      "03": encoding_2,
      "04": encoding_2,
      "05": encoding_2,
      "06": encoding_3,
      "07": encoding_4,
      "08": encoding_5,
      "09": encoding_6,
      "10": encoding_7,
      "11": encoding_8,
      "12": encoding_5,
      "13": encoding_5,
      "14": encoding_5,
      "15": encoding_8,
      "16": encoding_9,
      "17": encoding_10,
      "18": encoding_11,
      "19": encoding_12,
      "20": encoding_13,
      "21": encoding_14,
      "22": encoding_15,
      "23": encoding_16,
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
      else str(Config.__dict__[key]) for key in sorted(
        filter(lambda key: not key.startswith("__") and not isinstance(Config.__dict__[key], staticmethod),
          Config.__dict__))}))
  if args.loglevel:
    log.setLevel(args.loglevel.upper())

  if not check_config(log):
    log.error("Aborting evaluation because config is invalid")
    sys.exit(1)

  if args.test:
    log.warning("Config looks ok - aborting run")
    return

  # make sure the evaluation doesn't overwrite existing data
  evaluation_lock = "{}/has-eval".format(Config.EVALUATION_DIRECTORY)
  if os.path.exists(evaluation_lock):
    log.error("Aborting evaluation because directory {} already contains an evaluation!"
        .format(Config.EVALUATION_DIRECTORY))
    return
  open(evaluation_lock, "a").close() # touch eval lock

  try:
    log.warning("Starting evaluation '{}' (PID: {})".format(args.eid, os.getpid()))
    # fork as early as possible
    with Pool(processes=Config.PARALLEL_PROCESSES, initializer=ParallelGame.inject_log, initargs=(log,)) as pool:
      game = Game(pool, log)
      if Config.TOTAL_HANDS:
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
    log.error("Finished evaluation '{}' after {}".format(args.eid, time_string))
    logging.shutdown()

if __name__ == "__main__":
  main()
