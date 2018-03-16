#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from config import Config
from multiprocessing import current_process
from time import sleep

import numpy as np

import utils
from card import Card
from const import Const
from hand import Hand

LOG = None

class ParallelGame:

  def __init__(self, players):
    # NOTE: The players (their models) get updated because they still share the same reference
    self.players = players
    self._cards = [Card(suit, value) for suit in range(Const.PLAYER_COUNT) for value in range(Const.CARDS_PER_PLAYER)]
    self.dealer = 0
    self.current_score_team_1 = 0
    self.current_score_team_2 = 0

  @staticmethod
  def inject_log(log):
    global LOG # pylint: disable=global-statement
    LOG = log

  def play_hands(self, hands_to_play, already_played_hands):
    if Config.STORE_TRAINING_DATA or Config.ONLINE_TRAINING:
      training_data = np.ones((Const.DECISIONS_PER_HAND * Config.BATCH_SIZE, Const.CARDS_PER_HAND + 1), dtype=int)
    else:
      training_data = None
    last_to_index = 0
    checkpoint_data = list()
    batch_score_team_1 = 0
    batch_score_team_2 = 0
    batch_wins_team_1 = 0
    batch_wins_team_2 = 0
    checkpoint_score_team_1 = 0
    checkpoint_score_team_2 = 0
    checkpoint_wins_team_1 = 0
    checkpoint_wins_team_2 = 0

    LOG.debug("[{}]: Starting to play {} hands...".format(self._id, utils.format_human(hands_to_play)))
    for i in range(int(hands_to_play)):
      # set up and play new hand
      hand = Hand(self.players, self._cards, LOG)
      (score_team_1, score_team_2), winner = hand.play(self.dealer,
          self.current_score_team_1, self.current_score_team_2)

      # the next hand is started by the next player
      self.dealer = (self.dealer + 1) % Const.PLAYER_COUNT

      # update scores and win counts
      batch_score_team_1 += score_team_1
      batch_score_team_2 += score_team_2
      checkpoint_score_team_1 += score_team_1
      checkpoint_score_team_2 += score_team_2
      if winner:
        if winner == 1:
          batch_wins_team_1 += 1
          checkpoint_wins_team_1 += 1
        if winner == 2:
          batch_wins_team_2 += 1
          checkpoint_wins_team_2 += 1
        self.current_score_team_1 = 0
        self.current_score_team_2 = 0
      else:
        self.current_score_team_1 += score_team_1
        self.current_score_team_2 += score_team_2

      # update stats for current checkpoint
      if Config.STORE_SCORES and (i+1) % Config.CHECKPOINT_RESOLUTION == 0:
        checkpoint_data.append([i+1+already_played_hands, checkpoint_wins_team_1, checkpoint_score_team_1,
          checkpoint_wins_team_2, checkpoint_score_team_2,
          self.players[0].get_checkpoint_data(), self.players[1].get_checkpoint_data()
          ])

      if Config.STORE_TRAINING_DATA or Config.ONLINE_TRAINING:
        from_index = i * Const.DECISIONS_PER_HAND
        to_index = (i+1) * Const.DECISIONS_PER_HAND
        assert from_index == last_to_index
        last_to_index = to_index
        training_data[from_index:to_index] = hand.new_training_data

    LOG.debug("[{}]: ... finished playing {} hands".format(self._id, utils.format_human(hands_to_play)))

    # for row in training_data:
    #   assert row.sum() > 0
    return (batch_score_team_1, batch_score_team_2), (batch_wins_team_1, batch_wins_team_2), \
        training_data, checkpoint_data

  @staticmethod
  def set_seed_and_get_pid(worker_id):
    sleep(0.1)
    if Config.SEED:
      seed = Config.SEED + worker_id
      np.random.seed(seed)
    else:
      np.random.seed()
      seed = "random"
    pid = os.getpid()
    LOG.info("Found PID {} for worker {} (seed: {})".format(pid, worker_id, seed))
    return pid

  @property
  def _id(self):
    # pylint: disable=protected-access,not-callable
    if current_process()._identity:
      return current_process()._identity[0]
    return "0"
