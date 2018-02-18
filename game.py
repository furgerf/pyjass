#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import logging
import sys
import time

import numpy as np

import utils
from card import Card
from hand import Hand
from player import Player


class Game():

  def __init__(self):
    self.log = utils.get_logger("jass")
    self.log.setLevel("WARNING")
    self.cards = [Card(suit, value) for suit in range(4) for value in range(9)]
    self._total_score_team_1 = 0
    self._total_score_team_2 = 0

    self.team_1_strategy = "rf"
    self.team_2_strategy = "random"

    # self.team_1_strategy = "random"
    # self.team_2_strategy = "rf"

    self.p1 = Player("p1", self.team_1_strategy, self.log)
    self.p2 = Player("p2", self.team_2_strategy, self.log)
    self.p3 = Player("p3", self.team_1_strategy, self.log)
    self.p4 = Player("p4", self.team_2_strategy, self.log)

    self.p1.set_players(self.p4, self.p3, self.p2)
    self.p2.set_players(self.p1, self.p4, self.p3)
    self.p3.set_players(self.p2, self.p1, self.p4)
    self.p4.set_players(self.p3, self.p2, self.p1)

  def play(self, store_training_data=False):
    training_data = list() if store_training_data else None
    store_training_interval = int(5e4)
    warning_interval = int(5e4)
    total_hands = int(1e5)
    wins_team_1 = 0
    wins_team_2 = 0
    current_score_team_1 = 0
    current_score_team_2 = 0
    training_data_file_name="foo.csv"

    if training_data is not None:
      fh = open(training_data_file_name, "w")
      fh.write("36 rows for cards with their known state from the view of a player " + \
          "(0 unknown, 1-4 played by player, {} in play, {} in hand, {} selected to play; score of round from the view of the player\n"
        .format(Card.IN_PLAY, Card.IN_HAND, Card.SELECTED))
      writer = csv.writer(fh)

    dealer = 0
    for i in range(total_hands):
      if i % warning_interval == warning_interval-1:
        self.log.warning("Starting hand {}/{} ({:.2f}%)".format(i+1, total_hands, 100.0*(i+1)/total_hands))
      else:
        self.log.info("Starting hand {}".format(i+1))

      hand = Hand((self.p1, self.p2, self.p3, self.p4), self.cards, training_data, self.log)
      hand.play(dealer)
      dealer = (dealer + 1) % 4

      self._total_score_team_1 += hand.result[0]
      self._total_score_team_2 += hand.result[1]
      current_score_team_1 += hand.result[0]
      current_score_team_2 += hand.result[1]
      if current_score_team_1 > 1000 and current_score_team_2 > 1000:
        # "tie", count as no win for either team
        current_score_team_1 = 0
        current_score_team_2 = 0
      if current_score_team_1 > 1000:
        wins_team_1 += 1
        current_score_team_1 = 0
        current_score_team_2 = 0
      if current_score_team_2 > 1000:
        wins_team_2 += 1
        current_score_team_1 = 0
        current_score_team_2 = 0

      self.log.info("Result: {} vs {} ({} vs {})".format(hand.result[0], hand.result[1], self._total_score_team_1, self._total_score_team_2))
      if training_data is not None and i != 0 and i % store_training_interval == store_training_interval-1:
        self.log.warning("Writing {} training data entries to {}".format(len(training_data), fh.name))
        writer.writerows(training_data)
        training_data.clear()


    self.log.warning("Overall result: {} ({}) vs {} ({}); wins: {} vs {}; (score diff {}, off mean: {:.2f}%, win percentage: {:.2f}%)".format(
      self._total_score_team_1, self.team_1_strategy, self._total_score_team_2, self.team_2_strategy,
      wins_team_1, wins_team_2,
      int((self._total_score_team_1*2-(self._total_score_team_1+self._total_score_team_2))/2),
      100.0*(self._total_score_team_1*2-(self._total_score_team_1+self._total_score_team_2))/2/(self._total_score_team_1+self._total_score_team_2),
      100.0*wins_team_1/(wins_team_1+wins_team_2)))

    if training_data is not None:
      self.log.warning("Writing {} training data entries to {}".format(len(training_data), fh.name))
      writer.writerows(training_data)
      fh.close()

if __name__ == "__main__":
  # np.random.seed(42)
  game = None
  start_time = time.time()

  try:
    game = Game()
    game.play()
  except Exception as ex:
    game.log.critical("{} during evaluation: {}".format(type(ex).__name__, str(ex)))
    game.log.critical(traceback.format_exc())
    sys.exit(1)
  finally:
    mins, secs = divmod(time.time() - start_time, 60)
    hours, mins = divmod(mins, 60)
    time_string = \
        "{}h{}m{:.1f}s".format(int(hours), int(mins), secs) if hours > 0 else \
        "{}m{:.1f}s".format(int(mins), secs) if mins > 0 else \
        "{:.1f}s".format(secs)
    game.log.warning("Finished execution after {}".format(time_string))
    logging.shutdown()

