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

  PARALLEL_PROCESSES = 2 # constant for now
