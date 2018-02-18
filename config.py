#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Config:
  RANDOM = False
  LOG_LEVEL = "DEBUG"

  HAND_SCORE_FACTOR = 1

  STORE_TRAINING_DATA = True

  TEAM_1_STRATEGY = "rf"
  TEAM_2_STRATEGY = "random"

  TEAM_1_STRATEGY = "random"
  # TEAM_2_STRATEGY = "rf"

  STORE_TRAINING_INTERVAL = int(5e4)
  WARNING_INTERVAL = int(5e4)
  TOTAL_HANDS = int(1e5) * 0 + 1

  TRAINING_DATA_FILE_NAME = "foo.csv"

