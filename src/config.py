#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Config:
  # training/model
  SEED = None
  ENCODING = None
  STORE_TRAINING_DATA = False
  ONLINE_TRAINING = False
  STORE_SCORES = False

  # game configuration
  TEAM_1_STRATEGY = None
  TEAM_1_BEST = False
  TEAM_1_MODEL_ARGS = None
  TEAM_2_STRATEGY = None
  TEAM_2_BEST = False
  FORCE_GAME_TYPE = None

  # intervals
  TOTAL_HANDS = None
  TRAINING_INTERVAL = None
  CHECKPOINT_INTERVAL = None
  CHECKPOINT_RESOLUTION = None
  LOGGING_INTERVAL = None

  # files/directories
  MODEL_DIRECTORY = None
  REGRESSOR_NAME = None
  OTHER_REGRESSOR_NAME = None
  LOAD_TRAINING_DATA_FILE_NAME = None
  STORE_TRAINING_DATA_FILE_NAME = None
  EVALUATION_DIRECTORY = None
  LOSS_FILE = None

  # parallel processing
  PARALLEL_PROCESSES = None
  BATCH_SIZE = None
  BATCH_COUNT = None

  @staticmethod
  def set_batch_count():
    """
    Assigns the number of batches to the correct number depending on the other config entries.
    """
    Config.BATCH_COUNT = int(Config.TOTAL_HANDS / Config.BATCH_SIZE / Config.PARALLEL_PROCESSES)
