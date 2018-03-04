#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Config:
  # training/model
  ENCODING = None
  STORE_TRAINING_DATA = False
  ONLINE_TRAINING = False

  # game configuration
  TEAM_1_STRATEGY = None
  TEAM_1_BEST = False
  TEAM_2_STRATEGY = None
  TEAM_2_BEST = False

  # intervals
  TOTAL_HANDS = None
  LOGGING_INTERVAL = None
  TRAINING_INTERVAL = None
  CHECKPOINT_INTERVAL = None
  CHECKPOINT_RESOLUTION = None

  # files/directories
  MODEL_DIRECTORY = None
  REGRESSOR_NAME = None
  TRAINING_DATA_FILE_NAME = None
  EVALUATION_DIRECTORY = None

  # parallel processing
  PARALLEL_PROCESSES = 1 # constant for now
  BATCH_SIZE = None
  BATCH_COUNT = None

  @staticmethod
  def set_batch_parameters():
    Config.BATCH_SIZE = Config._batch_size()
    Config.BATCH_COUNT = Config._batch_count()

  @staticmethod
  def _batch_size(): # pylint: disable=invalid-name
    return int(min(Config.TRAINING_INTERVAL, Config.CHECKPOINT_INTERVAL) / Config.PARALLEL_PROCESSES) if \
        Config.STORE_TRAINING_DATA or Config.ONLINE_TRAINING else \
        int(Config.CHECKPOINT_INTERVAL / Config.PARALLEL_PROCESSES)

  @staticmethod
  def _batch_count(): # pylint: disable=invalid-name
    return int(Config.TOTAL_HANDS / Config.BATCH_SIZE / Config.PARALLEL_PROCESSES)
