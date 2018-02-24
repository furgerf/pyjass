#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Config:
  # TODO: Cleanup and only set those that are actually needed

  HAND_SCORE_FACTOR = 2

  STORE_TRAINING_DATA = False
  ONLINE_TRAINING = False

  TEAM_1_STRATEGY = None
  TEAM_1_BEST = False
  TEAM_2_STRATEGY = None
  TEAM_2_BEST = False

  TOTAL_HANDS = None
  LOGGING_INTERVAL = None
  TRAINING_INTERVAL = None
  CHECKPOINT_INTERVAL = None

  MODEL_DIRECTORY = "current-model"
  TRAINING_DATA_FILE_NAME = None
  EVALUATION_DIRECTORY = None
