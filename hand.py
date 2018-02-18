#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

import utils
from model import Mound
from round import Round


class Hand():

  def __init__(self, players, cards, training_data, log):
    self._players = players
    self.p1, self.p2, self.p3, self.p4 = players
    self._score_team_1 = 0
    self._score_team_2 = 0
    self._training_data = training_data
    self.log = log
    self._known_cards = np.zeros(36, dtype=int)

    # shuffle and distribute cards
    self.cards = np.random.permutation(cards)
    for i in range(len(self._players)):
      self._players[i].hand = self.cards[i*9:(i+1)*9]


  def play(self, dealer):
    """Plays the hand by playing 9 rounds.

    :dealer: (int) Index of the player that plays the first card.
    """

    # choose trump and set up cards accordingly
    trump = "obenabe"
    self.log.info("Playing hand with trump: {}".format(trump))
    [c.set_score(trump) for c in self.cards]

    training_data_team_1 = []
    training_data_team_2 = []

    for i in range(9):
      self.log.debug("---------- Round {} ----------".format(i+1))
      current_round = Round(self._players, self._known_cards, self.log,)
      dealer, score, played_cards, states = current_round.play(dealer)

      # update known cards - mark the cards that were played during this round
      for j in range(4):
        self._known_cards[played_cards[j].card_index] = j+1 # TODO: Check if this needs to be rotated and if some j should be an i
      self.log.debug("Known cards: {}".format(utils.format_cards(self._known_cards)))

      # update score
      if dealer % 2 == 0:
        self._score_team_1 += score
      else:
        self._score_team_2 += score

      # if we gather training data and actually had a decision to make, update training data
      if i < 8 and self._training_data is not None:
        self._update_current_training_data(training_data_team_1, training_data_team_2, states, score, dealer)

    # the hand is done, add 5 points for the last stich
    if dealer % 2 == 0:
      self.log.info("Team 1 made the last stich")
      self._score_team_1 += 5
    else:
      self.log.info("Team 2 made the last stich")
      self._score_team_2 += 5

    # after concluding the round, update the global training data
    if self._training_data is not None:
      for i in range(len(training_data_team_1)):
        training_data_team_1[i][-1] += self._score_team_1
      for i in range(len(training_data_team_2)):
        training_data_team_2[i][-1] += self._score_team_2
      self._training_data.extend(training_data_team_1)
      self._training_data.extend(training_data_team_2)

  def _update_current_training_data(self, training_data_team_1, training_data_team_2, states, score, dealer):
    if dealer % 2 == 0:
      training_data_team_1.append(np.append(states[0],  score * Model.HAND_SCORE_FACTOR))
      training_data_team_2.append(np.append(states[1], -score * Model.HAND_SCORE_FACTOR))
      training_data_team_1.append(np.append(states[2],  score * Model.HAND_SCORE_FACTOR))
      training_data_team_2.append(np.append(states[3], -score * Model.HAND_SCORE_FACTOR))
    else:
      training_data_team_1.append(np.append(states[0], -score * Model.HAND_SCORE_FACTOR))
      training_data_team_2.append(np.append(states[1],  score * Model.HAND_SCORE_FACTOR))
      training_data_team_1.append(np.append(states[2], -score * Model.HAND_SCORE_FACTOR))
      training_data_team_2.append(np.append(states[3],  score * Model.HAND_SCORE_FACTOR))

  @property
  def result(self):
    return (self._score_team_1, self._score_team_2)

