#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import utils
from config import Config
from const import Const
from round import Round


class Hand:
  def __init__(self, players, cards, log):
    self._players = players
    if Config.STORE_TRAINING_DATA or Config.ONLINE_TRAINING:
      self._training_data = list()
    self.log = log
    self._known_cards = np.zeros(Const.CARDS_PER_HAND, dtype=int)

    # shuffle and distribute cards
    self.cards = np.random.permutation(cards)
    for i in range(len(self._players)):
      self._players[i].hand = self.cards[i*Const.CARDS_PER_PLAYER:(i+1)*Const.CARDS_PER_PLAYER]


  def play(self, dealer, initial_score_team_1, initial_score_team_2):
    """Plays the hand by playing 9 rounds.

    :dealer: (int) Index of the player that plays the first card.
    """

    # choose trump and set up cards accordingly
    trump = "obenabe"
    self.log.debug("Playing hand with trump: {}".format(trump))
    [c.set_score(trump) for c in self.cards] # pylint: disable=expression-not-assigned

    _score_team_1 = 0
    _score_team_2 = 0
    training_data_team_1 = []
    training_data_team_2 = []
    winner = None

    for i in range(Const.CARDS_PER_PLAYER):
      self.log.debug("---------- Round {} ----------".format(i+1))
      current_round = Round(self._players, self._known_cards, self.log,)
      dealer, score, played_cards, states = current_round.play(dealer)

      # update known cards - mark the cards that were played during this round
      for j in range(Const.PLAYER_COUNT):
        assert self._known_cards[played_cards[j].card_index] == 0, "Can't change known card"
        self._known_cards[played_cards[j].card_index] = Config.ENCODING.card_code_players[j]
      self.log.debug("Known cards: {}".format(utils.format_cards(self._known_cards)))

      # update score
      if dealer % 2 == 0:
        _score_team_1 += score
        if not winner and _score_team_1 + initial_score_team_1 > Const.WINNING_SCORE:
          winner = 1
      else:
        _score_team_2 += score
        if not winner and _score_team_2 + initial_score_team_2 > Const.WINNING_SCORE:
          winner = 2

      # if we gather training data and actually had a decision to make, update training data
      if i < Const.CARDS_PER_PLAYER-1 and (Config.STORE_TRAINING_DATA or Config.ONLINE_TRAINING):
        Hand._update_current_training_data(training_data_team_1, training_data_team_2, states, score, dealer)

    # the hand is done, add 5 points for the last stich
    if dealer % 2 == 0:
      self.log.debug("Team 1 made the last stich")
      _score_team_1 += 5
      if not winner and _score_team_1 + initial_score_team_1 > Const.WINNING_SCORE:
        winner = 1
    else:
      self.log.debug("Team 2 made the last stich")
      _score_team_2 += 5
      if not winner and _score_team_2 + initial_score_team_2 > Const.WINNING_SCORE:
        winner = 2

    # after concluding the hand, update the global training data
    if Config.STORE_TRAINING_DATA or Config.ONLINE_TRAINING:
      for team_1_training_entry in training_data_team_1:
        team_1_training_entry[-1] += _score_team_1 * Config.ENCODING.hand_score_factor
      for team_2_training_entry in training_data_team_2:
        team_2_training_entry[-1] += _score_team_2 * Config.ENCODING.hand_score_factor

      # pylint: disable=consider-using-enumerate
      # for i in range(len(training_data_team_1)):
      #   self._training_data.append(training_data_team_1[i])
      #   self._training_data.append(training_data_team_2[i])
      self._training_data.extend(training_data_team_1)
      self._training_data.extend(training_data_team_2)

    return (_score_team_1, _score_team_2), winner

  @staticmethod
  def _update_current_training_data(training_data_team_1, training_data_team_2, states, score, dealer):
    if dealer % 2 == 0:
      training_data_team_1.append(np.append(states[0], score * Config.ENCODING.round_score_factor))
      training_data_team_2.append(np.append(states[1], -score * Config.ENCODING.round_score_factor))
      training_data_team_1.append(np.append(states[2], score * Config.ENCODING.round_score_factor))
      training_data_team_2.append(np.append(states[3], -score * Config.ENCODING.round_score_factor))
    else:
      training_data_team_1.append(np.append(states[0], -score * Config.ENCODING.round_score_factor))
      training_data_team_2.append(np.append(states[1], score * Config.ENCODING.round_score_factor))
      training_data_team_1.append(np.append(states[2], -score * Config.ENCODING.round_score_factor))
      training_data_team_2.append(np.append(states[3], score * Config.ENCODING.round_score_factor))

  @property
  def new_training_data(self):
    return self._training_data
