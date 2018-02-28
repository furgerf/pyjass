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

    self.players = (
        Game.PLAYER_TYPES[Config.TEAM_1_STRATEGY]("p1", Config.TEAM_1_BEST, self.log),
        Game.PLAYER_TYPES[Config.TEAM_2_STRATEGY]("p2", Config.TEAM_2_BEST, self.log),
        Game.PLAYER_TYPES[Config.TEAM_1_STRATEGY]("p3", Config.TEAM_1_BEST, self.log),
        Game.PLAYER_TYPES[Config.TEAM_2_STRATEGY]("p4", Config.TEAM_2_BEST, self.log)
        )

    self._wins_team_1 = 0
    self._wins_team_2 = 0
    self._ties = 0
    self._total_score_team_1 = 0
    self._total_score_team_2 = 0
    self._current_score_team_1 = 0
    self._current_score_team_2 = 0

    self._checkpoint_wins_team_1 = 0
    self._checkpoint_wins_team_2 = 0
    self._checkpoint_score_team_1 = 0
    self._checkpoint_score_team_2 = 0
    self._checkpoint_data = list()

    self._score_fh = None
    self._score_writer = None
    self._training_data_fh = None
    self._training_data_writer = None

  def play(self):
    self._score_fh = open("{}/scores.csv".format(Config.EVALUATION_DIRECTORY), "w")
    Game._write_scores_header(self._score_fh)
    self._score_writer = csv.writer(self._score_fh, lineterminator="\n")

    if Config.STORE_TRAINING_DATA:
      self._training_data_fh = open(Config.TRAINING_DATA_FILE_NAME, "w")
      Game._write_training_data_header(self._training_data_fh)
      self._training_data_writer = csv.writer(self._training_data_fh, lineterminator="\n")

    if Config.STORE_TRAINING_DATA or Config.ONLINE_TRAINING:
      training_data = list()

    dealer = 0
    if Config.STORE_TRAINING_DATA and Config.ONLINE_TRAINING:
      training_description = "(training online AND storing data)"
    elif Config.STORE_TRAINING_DATA:
      training_description = "(storing training data)"
    elif Config.ONLINE_TRAINING:
      training_description = "(training online)"
    else:
      training_description = ""

    self.log.error("Starting game of {} hands: {}{} vs {}{} {}".format(utils.format_human(Config.TOTAL_HANDS),
      Config.TEAM_1_STRATEGY, " (best)" if Config.TEAM_1_BEST else "",
      Config.TEAM_2_STRATEGY, " (best)" if Config.TEAM_2_BEST else "", training_description))
    for i in range(Config.TOTAL_HANDS):
      self.log.debug("Starting hand {}".format(i+1))

      # set up and play new hand
      hand = Hand(self.players, self._cards, self.log)
      score = hand.play(dealer)

      # the next hand is started by the next player
      dealer = (dealer + 1) % 4

      # update scores and win counts
      # TODO: Get rid of ties
      self._update_scores(*score)

      # logging
      if (i+1) % Config.LOGGING_INTERVAL == 0:
        self.log.info("Played hand {}/{} ({:.2f}% done)".format(
          utils.format_human(i+1), utils.format_human(Config.TOTAL_HANDS), 100.0*(i+1)/Config.TOTAL_HANDS))

      # handle new training data if required - train before checkpoint!
      if Config.STORE_TRAINING_DATA or Config.ONLINE_TRAINING:
        training_data.extend(hand.new_training_data)
        if (i+1) % Config.TRAINING_INTERVAL == 0:
          self._handle_training_data(training_data)

      # checkpoint
      self._update_checkpoint(i)

    # the game is over
    self._print_results()

    # deal with "leftover" data/cleanup
    if Config.STORE_TRAINING_DATA or Config.ONLINE_TRAINING:
      self._handle_training_data(training_data)
    if Config.STORE_TRAINING_DATA:
      self._training_data_fh.close()
    self._create_checkpoint(Config.TOTAL_HANDS, Config.TOTAL_HANDS)


  def _update_scores(self, score_team_1, score_team_2):
    self._total_score_team_1 += score_team_1
    self._total_score_team_2 += score_team_2
    self._current_score_team_1 += score_team_1
    self._current_score_team_2 += score_team_2
    self._checkpoint_score_team_1 += score_team_1
    self._checkpoint_score_team_2 += score_team_2
    if self._current_score_team_1 > 1000 or self._current_score_team_2 > 1000:
      if self._current_score_team_1 > 1000 and self._current_score_team_2 > 1000:
        self._ties += 1
      elif self._current_score_team_1 > 1000:
        self._wins_team_1 += 1
        self._checkpoint_wins_team_1 += 1
      elif self._current_score_team_2 > 1000:
        self._wins_team_2 += 1
        self._checkpoint_wins_team_2 += 1
      self._current_score_team_1 = 0
      self._current_score_team_2 = 0

    self.log.debug("Result: {} vs {} ({} vs {})".format(score_team_1,
      score_team_2, self._total_score_team_1, self._total_score_team_2))

  def _handle_training_data(self, training_data):
    if not training_data:
      return

    if Config.STORE_TRAINING_DATA:
      self._write_training_data(training_data)
    if Config.ONLINE_TRAINING:
      for player in self._get_distinct_strategy_players():
        player.train(training_data)
    training_data.clear()

  def _update_checkpoint(self, i):
    if (i+1) % Config.CHECKPOINT_RESOLUTION == 0:
      self._checkpoint_data.append([i+1, self._checkpoint_wins_team_1, self._checkpoint_score_team_1,
        self._checkpoint_wins_team_2, self._checkpoint_score_team_2,
        self.players[0].get_checkpoint_data(), self.players[1].get_checkpoint_data()
        ])
    if (i+1) % Config.CHECKPOINT_INTERVAL == 0:
      self._create_checkpoint(i+1, Config.TOTAL_HANDS)
      self._checkpoint_wins_team_1 = 0
      self._checkpoint_wins_team_2 = 0
      self._checkpoint_score_team_1 = 0
      self._checkpoint_score_team_2 = 0
      self._checkpoint_data.clear()

  def _create_checkpoint(self, current_iteration, total_iterations):
    if not self._checkpoint_data:
      return

    self.log.warning("Creating checkpoint with {} scores at iteration {}/{}"
        .format(utils.format_human(len(self._checkpoint_data)),
          utils.format_human(current_iteration), utils.format_human(total_iterations)))
    self._score_writer.writerows(self._checkpoint_data)
    self._score_fh.flush()

    for player in self._get_distinct_strategy_players():
      player.checkpoint(current_iteration, total_iterations)

  def _get_distinct_strategy_players(self):
    if Config.TEAM_1_STRATEGY == Config.TEAM_2_STRATEGY:
      return [self.players[0]]
    return [self.players[0], self.players[1]]

  @staticmethod
  def _write_scores_header(fh):
    header = "hand,wins_team_1,score_team_1,wins_team_2,score_team_2,team_1_info,team_2_info\n"
    fh.write(header)

  @staticmethod
  def _write_training_data_header(fh):
    header = "36 rows for cards with their known state from the view of a player " + \
        "(0 unknown, {} played by player, {} in play, {} in hand, {} selected to play; " + \
        "score of round from the view of the player: round factor {}, hand factor {}\n"
    fh.write(header.format(Config.ENCODING.card_code_players, Config.ENCODING.card_code_in_play,
      Config.ENCODING.card_code_in_hand, Config.ENCODING.card_code_selected,
      Config.ENCODING.round_score_factor, Config.ENCODING.hand_score_factor))

  def _write_training_data(self, training_data):
    if not training_data:
      return
    self.log.info("Writing {} training samples to {}".format(
      utils.format_human(len(training_data)), self._training_data_fh.name))
    self._training_data_writer.writerows(training_data)

  def _print_results(self):
    # all hands are played
    score_of_both_teams = self._total_score_team_1 + self._total_score_team_2
    wins_of_both_teams = self._wins_team_1 + self._wins_team_2
    message = "Overall result: {} ({}) vs {} ({}); wins: {} vs {} ({} ties); " + \
        "(score diff {}, off mean: {:.2f}%, T1 win percentage: {:.2f}%)"
    self.log.error(message.format(
      utils.format_human(self._total_score_team_1), Config.TEAM_1_STRATEGY,
      utils.format_human(self._total_score_team_2), Config.TEAM_2_STRATEGY,
      utils.format_human(self._wins_team_1), utils.format_human(self._wins_team_2), utils.format_human(self._ties),
      utils.format_human((self._total_score_team_1*2-score_of_both_teams)/2),
      100.0*(self._total_score_team_1*2-score_of_both_teams)/2/score_of_both_teams,
      100.0*self._wins_team_1/wins_of_both_teams if wins_of_both_teams > 0 else 0))
