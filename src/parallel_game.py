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
from game_type import GameType
from hand import Hand
from score import Score

LOG = None

class ParallelGame:

  def __init__(self, players):
    # NOTE: The players (their models) get updated because they still share the same reference
    self.players = players

    self._cards = [Card(suit, value) for suit in range(len(Card.SUITS)) for value in range(len(Card.VALUES))]
    self.dealer = 0

    # the "current score" is the score of the current, ongoing game
    self.current_score_team_1 = 0
    self.current_score_team_2 = 0

  @staticmethod
  def inject_log(log):
    global LOG # pylint: disable=global-statement
    LOG = log

  def play_hands(self, already_played_hands):
    if Config.STORE_TRAINING_DATA or Config.ONLINE_TRAINING:
      # samples per game times number of games, number of cards plus score
      training_data = np.ones((Const.DECISIONS_PER_HAND * Config.BATCH_SIZE, Const.CARDS_PER_HAND + 1), dtype=int)
      # number of games, number of initial hand cards plus chosen game type and score
      game_type_decisions = np.ones((Config.BATCH_SIZE, Const.CARDS_PER_PLAYER + 2), dtype=int)
    else:
      training_data = None
      game_type_decisions = None
    last_to_index = 0
    checkpoint_data = list()
    batch_score = Score()
    checkpoint_score = Score()
    selected_game_types = np.zeros((Const.PLAYER_COUNT, len(GameType)), dtype=int)

    LOG.debug("[{}]: Starting to play {} hands...".format(self._id, utils.format_human(Config.BATCH_SIZE)))
    for i in range(int(Config.BATCH_SIZE)):
      # set up and play new hand
      # NOTE: we're always playing witht he same cards and expect that the game type and scores get overwritten
      hand = Hand(self.players, self._cards, LOG)
      (score_team_1, score_team_2), winner, game_type = hand.play(self.dealer,
          self.current_score_team_1, self.current_score_team_2)
      selected_game_types[self.dealer, game_type.value] += 1

      # the next hand is started by the next player
      self.dealer = (self.dealer + 1) % Const.PLAYER_COUNT

      # update scores and win counts
      batch_score.add_scores(score_team_1, score_team_2)
      checkpoint_score.add_scores(score_team_1, score_team_2)
      if winner:
        batch_score.add_win(winner == 1)
        checkpoint_score.add_win(winner == 1)
        self.current_score_team_1 = 0
        self.current_score_team_2 = 0
      else:
        self.current_score_team_1 += score_team_1
        self.current_score_team_2 += score_team_2

      # update stats for current checkpoint
      if Config.STORE_SCORES and (i+1) % Config.CHECKPOINT_RESOLUTION == 0:
        checkpoint_data.append([i+1+already_played_hands, *checkpoint_score.score_data,
          self.players[0].get_checkpoint_data(), self.players[1].get_checkpoint_data()
          ])
        checkpoint_score.clear()

      if Config.STORE_TRAINING_DATA or Config.ONLINE_TRAINING:
        from_index = i * Const.DECISIONS_PER_HAND
        to_index = (i+1) * Const.DECISIONS_PER_HAND
        assert from_index == last_to_index
        last_to_index = to_index
        training_data[from_index:to_index] = hand.new_training_data
        game_type_decisions[i] = hand.game_type_decision

    LOG.debug("[{}]: ... finished playing {} hands".format(self._id, utils.format_human(Config.BATCH_SIZE)))

    return batch_score, training_data, game_type_decisions, checkpoint_data, selected_game_types

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
    LOG.debug("Found PID {} for worker {} (seed: {})".format(pid, worker_id, seed))
    return pid

  @property
  def _id(self):
    # pylint: disable=protected-access,not-callable
    process_identity = current_process()._identity
    return process_identity[0] if process_identity else "0"
