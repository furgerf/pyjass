#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import numpy as np

import utils
from card import Card
from hand import Hand
from player import Player


class Game():

  def __init__(self):
    self.log = utils.get_logger("jass")
    # self.log.setLevel("INFO")
    self.cards = [Card(suit, value) for suit in range(4) for value in range(9)]
    self._total_score_team_1 = 0
    self._total_score_team_2 = 0

    self.p1 = Player("p1", self.log)
    self.p2 = Player("p2", self.log)
    self.p3 = Player("p3", self.log)
    self.p4 = Player("p4", self.log)

    self.p1.set_players(self.p4, self.p3, self.p2)
    self.p2.set_players(self.p1, self.p4, self.p3)
    self.p3.set_players(self.p2, self.p1, self.p4)
    self.p4.set_players(self.p3, self.p2, self.p1)

  def play(self):
    for i in range(1):
      self.log.info("Starting hand {}".format(i+1))
      hand = Hand((self.p1, self.p2, self.p3, self.p4), self.cards, self.log)
      if i > 0:
        sys.stdin.read(1)
      hand.play()
      self._total_score_team_1 += hand.result[0]
      self._total_score_team_2 += hand.result[1]
      self.log.info("Result: {} vs {} ({} vs {})".format(hand.result[0], hand.result[1], self._total_score_team_1, self._total_score_team_2))

if __name__ == "__main__":
  np.random.seed(42)
  game = Game()
  game.play()

