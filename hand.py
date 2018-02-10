#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

import utils
from round import Round


class Hand():

  def __init__(self, players, cards, training_data, log):
    self._players = players
    self.p1, self.p2, self.p3, self.p4 = players
    self._score_team_1 = 0
    self._score_team_2 = 0
    self._training_data = training_data
    self.log = log

    # shuffle
    self.cards = np.random.permutation(cards)
    # distribute
    for i in range(len(self._players)):
      self._players[i].hand = self.cards[i*9:(i+1)*9]

    self._known_cards = np.zeros(36, dtype=int)

  def play(self):
    # choose trump
    trump = "obenabe"
    [c.set_score(trump) for c in self.cards]
    self.log.info("Playing hand with trump: {}".format(trump))

    # p1 begins
    dealer = 0
    for i in range(9):
      self.log.debug("---------- Round {} ----------".format(i+1))
      current_round = Round(self._players, self._known_cards, self.log,)
      dealer, played_cards, score, states = current_round.play(dealer)
      for i in range(4):
        self._known_cards[played_cards[i].card_index] = i+1
      self.log.debug("Known cards: {}".format(utils.format_cards(self._known_cards)))
      if dealer % 2 == 0:
        self._score_team_1 += score
        if self._training_data:
          self._training_data.append(np.append(states[0],  score))
          self._training_data.append(np.append(states[1], -score))
          self._training_data.append(np.append(states[2],  score))
          self._training_data.append(np.append(states[3], -score))
      else:
        self._score_team_2 += score
        if self._training_data:
          self._training_data.append(np.append(states[0], -score))
          self._training_data.append(np.append(states[1],  score))
          self._training_data.append(np.append(states[2], -score))
          self._training_data.append(np.append(states[3],  score))

    if dealer % 2 == 0:
      self.log.info("Team 1 made the last stich")
      self._score_team_1 += 5
    else:
      self.log.info("Team 2 made the last stich")
      self._score_team_2 += 5

  @property
  def result(self):
    return (self._score_team_1, self._score_team_2)

