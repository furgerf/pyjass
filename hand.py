#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from round import Round

class Hand():

  def __init__(self, players, cards):
    self._players = players
    self.p1, self.p2, self.p3, self.p4 = players
    self._score_team_1 = 0
    self._score_team_2 = 0

    # shuffle
    self.cards = np.random.permutation(cards)
    # distribute
    for i in range(len(self._players)):
      self._players[i].hand = self.cards[i*9:(i+1)*9]

  def play(self):
    # choose trump
    trump = "obenabe"
    [c.set_score(trump) for c in self.cards]
    print("Playing hand with trump: {}".format(trump))

    # p1 begins
    dealer = 0
    for i in range(9):
      print("\nRound {}".format(i+1))
      current_round = Round(self._players)
      dealer = current_round.play(dealer)
      if dealer % 2 == 0:
        self._score_team_1 += current_round.score
      else:
        self._score_team_2 += current_round.score

    if dealer % 2 == 0:
      print("\nTeam 1 made the last stich")
      self._score_team_1 += 5
    else:
      print("\nTeam 2 made the last stich")
      self._score_team_2 += 5

  @property
  def result(self):
    return (self._score_team_1, self._score_team_2)

