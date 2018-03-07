#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from multiprocessing import current_process
from time import sleep

import utils
from card import Card
from config import Config
from hand import Hand

LOG = None

class ParallelGame:

  def __init__(self, players):
    # NOTE: The players (their models) get updated because they still share the same reference
    self.players = players
    self._cards = [Card(suit, value) for suit in range(4) for value in range(9)]

  @staticmethod
  def inject_log(log):
    global LOG # pylint: disable=global-statement
    LOG = log

  def play_hands(self, hands_to_play, already_played_hands, dealer, scores):
    # TODO: Try improving memory consumption with pre-allocated (numpy) arrays
    training_data = list()
    checkpoint_data = list()
    current_score_team_1, current_score_team_2 = scores
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
      (score_team_1, score_team_2), winner = hand.play(dealer, current_score_team_1, current_score_team_2)

      # the next hand is started by the next player
      dealer = (dealer + 1) % 4

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
        current_score_team_1 = 0
        current_score_team_2 = 0
      else:
        current_score_team_1 += score_team_1
        current_score_team_2 += score_team_2

      # update stats for current checkpoint
      if Config.STORE_SCORES and (i+1) % Config.CHECKPOINT_RESOLUTION == 0:
        checkpoint_data.append([i+1+already_played_hands, checkpoint_wins_team_1, checkpoint_score_team_1,
          checkpoint_wins_team_2, checkpoint_score_team_2,
          self.players[0].get_checkpoint_data(), self.players[1].get_checkpoint_data()
          ])

      if Config.STORE_TRAINING_DATA or Config.ONLINE_TRAINING:
        training_data.extend(hand.new_training_data)

    LOG.debug("[{}]: ... finished playing {} hands".format(self._id, utils.format_human(hands_to_play)))

    return dealer, (current_score_team_1, current_score_team_2), (batch_score_team_1, batch_score_team_2), \
        (batch_wins_team_1, batch_wins_team_2), checkpoint_data, training_data

  @staticmethod
  def pid():
    sleep(0.1)
    return os.getpid()

  @property
  def _id(self):
    if current_process()._identity:
      return current_process()._identity[0] # pylint: disable=protected-access,not-callable
    return "0"
