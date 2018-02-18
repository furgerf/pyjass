#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
from config import Config

import utils
from baseline_players import HighestCardPlayer, RandomCardPlayer
from card import Card
from hand import Hand
from learner_players import MlpPlayer, SgdPlayer


class Game:
  PLAYER_TYPES = {
      "random": RandomCardPlayer,
      "highest": HighestCardPlayer,
      "sgd": SgdPlayer,
      "mlp": MlpPlayer
      }

  def __init__(self, log):
    self.log = log
    self._cards = [Card(suit, value) for suit in range(4) for value in range(9)]
    self._total_score_team_1 = 0
    self._total_score_team_2 = 0

    self.players = (
        Game.PLAYER_TYPES[Config.TEAM_1_STRATEGY]("p1", self.log),
        Game.PLAYER_TYPES[Config.TEAM_2_STRATEGY]("p2", self.log),
        Game.PLAYER_TYPES[Config.TEAM_1_STRATEGY]("p3", self.log),
        Game.PLAYER_TYPES[Config.TEAM_2_STRATEGY]("p4", self.log)
        )

  def play(self):
    wins_team_1 = 0
    wins_team_2 = 0
    ties = 0
    current_score_team_1 = 0
    current_score_team_2 = 0

    if Config.STORE_TRAINING_DATA:
      fh = open(Config.TRAINING_DATA_FILE_NAME, "w")
      Game._write_training_data_header(fh)
      writer = csv.writer(fh)
      training_data = list()

    dealer = 0
    self.log.warning("Starting game of {} hands: {} vs {}{}".format(utils.format_human(Config.TOTAL_HANDS),
      Config.TEAM_1_STRATEGY, Config.TEAM_2_STRATEGY, " (storing training data)" if Config.STORE_TRAINING_DATA else ""))
    for i in range(Config.TOTAL_HANDS):
      if i % Config.LOGGING_INTERVAL == Config.LOGGING_INTERVAL-1:
        self.log.info("Starting hand {}/{} ({:.2f}%)".format(
          utils.format_human(i+1), utils.format_human(Config.TOTAL_HANDS), 100.0*(i+1)/Config.TOTAL_HANDS))
      else:
        self.log.debug("Starting hand {}".format(i+1))

      # set up and play new hand
      hand = Hand(self.players, self._cards, self.log)
      score = hand.play(dealer)

      # the next hand is started by the next player
      dealer = (dealer + 1) % 4

      # update scores and check if a game was won
      self._total_score_team_1 += score[0]
      self._total_score_team_2 += score[1]
      current_score_team_1 += score[0]
      current_score_team_2 += score[1]
      if current_score_team_1 > 1000 or current_score_team_2 > 1000:
        if current_score_team_1 > 1000 and current_score_team_2 > 1000:
          ties += 1
        elif current_score_team_1 > 1000:
          wins_team_1 += 1
        elif current_score_team_2 > 1000:
          wins_team_2 += 1
        current_score_team_1 = 0
        current_score_team_2 = 0

      self.log.debug("Result: {} vs {} ({} vs {})".format(score[0],
        score[1], self._total_score_team_1, self._total_score_team_2))

      # handle new training data if required
      if Config.STORE_TRAINING_DATA:
        training_data.extend(hand.new_training_data)
        if i != 0 and i % Config.STORE_TRAINING_INTERVAL == Config.STORE_TRAINING_INTERVAL-1:
          self._write_training_data(fh, writer, training_data)

    self._print_results(wins_team_1, wins_team_2, ties)

    if Config.STORE_TRAINING_DATA:
      self._write_training_data(fh, writer, training_data)
      fh.close()

  @staticmethod
  def _write_training_data_header(fh):
    header = "36 rows for cards with their known state from the view of a player " + \
        "(0 unknown, 1-4 played by player, {} in play, {} in hand, {} selected to play; " + \
        "score of round from the view of the player\n"
    fh.write(header.format(Card.IN_PLAY, Card.IN_HAND, Card.SELECTED))

  def _write_training_data(self, fh, writer, training_data):
    if not training_data:
      return
    self.log.info("Writing {} training samples to {}".format(len(training_data), fh.name))
    writer.writerows(training_data)
    training_data.clear()

  def _print_results(self, wins_team_1, wins_team_2, ties):
    # all hands are played
    score_of_both_teams = self._total_score_team_1 + self._total_score_team_2
    wins_of_both_teams = wins_team_1 + wins_team_2
    message = "Overall result: {} ({}) vs {} ({}); wins: {} vs {} ({} ties); " + \
        "(score diff {}, off mean: {:.2f}%, T1 win percentage: {:.2f}%)"
    self.log.warning(message.format(
      utils.format_human(self._total_score_team_1), Config.TEAM_1_STRATEGY,
      utils.format_human(self._total_score_team_2), Config.TEAM_2_STRATEGY,
      utils.format_human(wins_team_1), utils.format_human(wins_team_2), utils.format_human(ties),
      utils.format_human((self._total_score_team_1*2-score_of_both_teams)/2),
      100.0*(self._total_score_team_1*2-score_of_both_teams)/2/score_of_both_teams,
      100.0*wins_team_1/wins_of_both_teams if wins_of_both_teams > 0 else 0))
