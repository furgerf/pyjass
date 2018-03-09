#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
from multiprocessing import Pool

import numpy as np
import utils
from baseline_players import (HighestCardPlayer, RandomCardPlayer,
                              SimpleRulesPlayer)
from config import Config
from learner_players import MlpPlayer, SgdPlayer
from parallel_game import ParallelGame
from psutil import Process


class Game:
  PLAYER_TYPES = {
      "random": RandomCardPlayer,
      "highest": HighestCardPlayer,
      "simple": SimpleRulesPlayer,
      "sgd": SgdPlayer,
      "mlp": MlpPlayer
      }

  def __init__(self, log):
    self.log = log
    self.players = (
        Game.PLAYER_TYPES[Config.TEAM_1_STRATEGY]("p1", Config.TEAM_1_BEST, self.log),
        Game.PLAYER_TYPES[Config.TEAM_2_STRATEGY]("p2", Config.TEAM_2_BEST, self.log),
        Game.PLAYER_TYPES[Config.TEAM_1_STRATEGY]("p3", Config.TEAM_1_BEST, self.log),
        Game.PLAYER_TYPES[Config.TEAM_2_STRATEGY]("p4", Config.TEAM_2_BEST, self.log)
        )

    self._wins_team_1 = 0
    self._wins_team_2 = 0
    self._total_score_team_1 = 0
    self._total_score_team_2 = 0
    self._current_score_team_1 = 0
    self._current_score_team_2 = 0

    if Config.STORE_SCORES:
      self._checkpoint_data = list()
      self._checkpoint_wins_team_1 = 0
      self._checkpoint_wins_team_2 = 0
      self._checkpoint_score_team_1 = 0
      self._checkpoint_score_team_2 = 0

    self._score_fh = None
    self._score_writer = None
    self._training_data_fh = None
    self._training_data_writer = None

  def initialize(self):
    if Config.STORE_SCORES:
      self._score_fh = open("{}/scores.csv".format(Config.EVALUATION_DIRECTORY), "w")
      Game._write_scores_header(self._score_fh)
      self._score_writer = csv.writer(self._score_fh, lineterminator="\n")

    if Config.STORE_TRAINING_DATA:
      self._training_data_fh = open(Config.TRAINING_DATA_FILE_NAME, "w")
      Game._write_training_data_header(self._training_data_fh)
      self._training_data_writer = csv.writer(self._training_data_fh, lineterminator="\n")

    if Config.STORE_TRAINING_DATA and Config.ONLINE_TRAINING:
      training_description = "(training online AND storing data)"
    elif Config.STORE_TRAINING_DATA:
      training_description = "(storing training data)"
    elif Config.ONLINE_TRAINING:
      training_description = "(training online)"
    else:
      training_description = ""
    self.log.error("Starting game of {} hands: {}{} vs {}{} {} ({} processes, {} batch size, {} rounds)"
        .format(utils.format_human(Config.TOTAL_HANDS),
      Config.TEAM_1_STRATEGY, " (best)" if Config.TEAM_1_BEST else "",
      Config.TEAM_2_STRATEGY, " (best)" if Config.TEAM_2_BEST else "", training_description,
      Config.PARALLEL_PROCESSES, utils.format_human(Config.BATCH_SIZE), utils.format_human(Config.BATCH_COUNT)))


  def play(self):
    self.initialize()

    played_hands = 0
    batch_round = 0
    parallel_games = [ParallelGame(self.players) for _ in range(Config.PARALLEL_PROCESSES)]
    last_to_index = 0

    if Config.STORE_TRAINING_DATA or Config.ONLINE_TRAINING:
      training_samples_per_batch = 32*Config.BATCH_SIZE
      training_samples_per_training = 32*Config.TRAINING_INTERVAL
      training_data = np.ones((training_samples_per_training, 37), dtype=int)

    with Pool(processes=Config.PARALLEL_PROCESSES, initializer=ParallelGame.inject_log, initargs=(self.log,)) as pool:
      # retrieve processes
      results = [pool.apply_async(ParallelGame.pid, ()) for i in range(Config.PARALLEL_PROCESSES)]
      pool_pids = [result.get() for result in results]
      assert len(set(pool_pids)) == len(pool_pids)
      pids = [os.getpid()] + pool_pids
      self.log.info("Found 1+{} processes: {}".format(len(pids)-1, " ".join(str(p) for p in pids)))
      processes = [Process(pid) for pid in pids]

      while played_hands < Config.TOTAL_HANDS:
        self.log.debug("Starting batch {}".format(batch_round+1))
        if Config.PARALLEL_PROCESSES > 1:
          batch = [pool.apply_async(game.play_hands, (Config.BATCH_SIZE, played_hands + i * Config.BATCH_SIZE))
            for i, game in enumerate(parallel_games)]
          self.log.debug("Started parallel batch of size {}".format(utils.format_human(Config.BATCH_SIZE)))
          results = [b.get() for b in batch]
        else:
          ParallelGame.inject_log(self.log)
          self.log.debug("Starting sequential batch of size {}".format(utils.format_human(Config.BATCH_SIZE)))
          results = [game.play_hands(Config.BATCH_SIZE, played_hands + i * Config.BATCH_SIZE)
              for i, game in enumerate(parallel_games)]

        self.log.debug("Processing results of batch")
        self._total_score_team_1 += sum(map(lambda result: result[2][0], results))
        self._total_score_team_2 += sum(map(lambda result: result[2][1], results))
        self._wins_team_1 += sum(map(lambda result: result[3][0], results))
        self._wins_team_2 += sum(map(lambda result: result[3][1], results))

        played_hands += Config.BATCH_SIZE * Config.PARALLEL_PROCESSES
        batch_round += 1

        # handle new training data if required - train before checkpoint!
        if Config.STORE_TRAINING_DATA or Config.ONLINE_TRAINING:
          start_index = int(((played_hands - Config.BATCH_SIZE * Config.PARALLEL_PROCESSES)
            % Config.TRAINING_INTERVAL) / Config.BATCH_SIZE)
          for i, result in enumerate(results):
            from_index = (start_index+i) * training_samples_per_batch
            to_index = (start_index+i+1) * training_samples_per_batch
            assert from_index == last_to_index
            last_to_index = to_index % len(training_data)
            training_data[from_index:to_index] = result[5]
          if played_hands % Config.TRAINING_INTERVAL == 0:
            # for row in training_data:
            #   assert row.sum() > 0
            self._handle_training_data(training_data)

        # checkpoint
        if Config.STORE_SCORES:
          for result in results:
            self._checkpoint_data.extend(result[4])
        if played_hands % Config.CHECKPOINT_INTERVAL == 0:
          self._create_checkpoint(played_hands, Config.TOTAL_HANDS)
          if Config.STORE_SCORES:
            self._checkpoint_data.clear()

        # logging
        if played_hands % Config.LOGGING_INTERVAL == 0:
          memory = [round(process.memory_info().rss/1e6, 1) for process in processes]
          self.log.info("Finished round {}/{} ({:.1f}%), hands: {}/{}, memory: {}={:.1f}M".format(
            utils.format_human(batch_round), utils.format_human(Config.BATCH_COUNT),
            100.0*batch_round/Config.BATCH_COUNT,
            utils.format_human(played_hands), utils.format_human(Config.TOTAL_HANDS),
            "+".join(str(m) for m in memory), sum(memory)))

    # the game is over
    self._print_results()

    # cleanup
    if self._training_data_fh:
      self._training_data_fh.close()
    if self._score_fh:
      self._score_fh.close()

  def _handle_training_data(self, training_data):
    if Config.STORE_TRAINING_DATA:
      self._write_training_data(training_data)
    if Config.ONLINE_TRAINING:
      for player in self._get_distinct_strategy_players():
        player.train(training_data, self.log)

  def _create_checkpoint(self, current_iteration, total_iterations):
    if Config.STORE_SCORES:
      self.log.warning("Writing {} scores at iteration {}/{} ({:.1f}%)"
          .format(utils.format_human(len(self._checkpoint_data)),
            utils.format_human(current_iteration), utils.format_human(total_iterations),
            100.0*current_iteration/total_iterations))
      self._score_writer.writerows(self._checkpoint_data)
      self._score_fh.flush()
    if Config.ONLINE_TRAINING:
      for player in self._get_distinct_strategy_players():
        player.checkpoint(current_iteration, total_iterations, self.log)

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
    message = "Overall result: {} ({}{}) vs {} ({}{}); wins: {} vs {}; " + \
        "(score diff {}, off mean: {:.2f}%, T1 win percentage: {:.2f}%)"
    self.log.error(message.format(
      utils.format_human(self._total_score_team_1), Config.TEAM_1_STRATEGY, " (best)" if Config.TEAM_1_BEST else "",
      utils.format_human(self._total_score_team_2), Config.TEAM_2_STRATEGY, " (best)" if Config.TEAM_2_BEST else "",
      utils.format_human(self._wins_team_1), utils.format_human(self._wins_team_2),
      utils.format_human((self._total_score_team_1*2-score_of_both_teams)/2),
      100.0*(self._total_score_team_1*2-score_of_both_teams)/2/score_of_both_teams,
      100.0*self._wins_team_1/wins_of_both_teams if wins_of_both_teams > 0 else 0))
