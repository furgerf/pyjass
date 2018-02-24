#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Config:
  HAND_SCORE_FACTOR = 2

  STORE_TRAINING_DATA = False

  TEAM_1_STRATEGY = None
  TEAM_2_STRATEGY = None

  TOTAL_HANDS = None
  LOGGING_INTERVAL = None
  STORE_TRAINING_INTERVAL = None

  MODEL_DIRECTORY = "current-model"
  TRAINING_DATA_FILE_NAME = None
  EVALUATION_DIRECTORY = None
