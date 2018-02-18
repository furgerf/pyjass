#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Config:
  RANDOM = False

  LOG_LEVEL = "DEBUG"
  LOG_LEVEL = "WARNING"

  HAND_SCORE_FACTOR = 2

  STORE_TRAINING_DATA = True

  TEAM_1_STRATEGY = "rf"
  TEAM_2_STRATEGY = "random"

  TEAM_1_STRATEGY = "random"
  # TEAM_2_STRATEGY = "rf"

  STORE_TRAINING_INTERVAL = int(1e4)
  LOGGING_INTERVAL = int(5e4)
  TOTAL_HANDS = int(1e6) * 1 + 0

  TRAINING_DATA_FILE_NAME = "data/foo.csv"

