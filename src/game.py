#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
import struct
import time
from datetime import datetime, timedelta

import numpy as np
from psutil import Process

import utils
from baseline_players import HighestCardPlayer, RandomCardPlayer
from better_rules_player import BetterRulesPlayer
from config import Config
from const import Const
from fixed_better_rules_player import FixedBetterRulesPlayer
from game_type import GameType
from keras_player import KerasPlayer
from parallel_game import ParallelGame
from score import Score
from simple_rules_player import SimpleRulesPlayer
from sklearn_player import MlpPlayer, OtherMlpPlayer, SgdPlayer


class Game:
  PLAYER_TYPES = {
      "random": RandomCardPlayer,
      "highest": HighestCardPlayer,
      "simple": SimpleRulesPlayer,
      "better": BetterRulesPlayer,
      "fixed-better": FixedBetterRulesPlayer,
      "baseline": None,
      "sgd": SgdPlayer,
      "mlp": MlpPlayer,
      "mlp-other": OtherMlpPlayer,
      "keras": KerasPlayer
      }

  def __init__(self, pool, log):
    self.pool = pool
    self.log = log

    Game.PLAYER_TYPES["baseline"] = Game.PLAYER_TYPES[Config.ENCODING.baseline]
    self.players = (
        Game.PLAYER_TYPES[Config.TEAM_1_STRATEGY]("p1", Config.ENCODING.card_code_players[0], self.log),
        Game.PLAYER_TYPES[Config.TEAM_2_STRATEGY]("p2", Config.ENCODING.card_code_players[1], self.log),
        Game.PLAYER_TYPES[Config.TEAM_1_STRATEGY]("p3", Config.ENCODING.card_code_players[2], self.log),
        Game.PLAYER_TYPES[Config.TEAM_2_STRATEGY]("p4", Config.ENCODING.card_code_players[3], self.log)
        )

    self._overall_score = Score()
    self._selected_game_types = np.zeros((Const.PLAYER_COUNT, len(GameType)), dtype=int)

    if Config.STORE_SCORES:
      self._checkpoint_data = list()

    self._score_fh = None
    self._score_writer = None
    self._training_data_fh = None
    self._game_type_decisions_fh = None
    self._training_data_writer = None

  def initialize(self):
    if Config.STORE_SCORES:
      self._score_fh = open("{}/scores.csv".format(Config.EVALUATION_DIRECTORY), "w")
      self._write_scores_header()
      self._score_writer = csv.writer(self._score_fh, lineterminator="\n")

    if Config.STORE_TRAINING_DATA:
      self._training_data_fh = open(Config.STORE_TRAINING_DATA_FILE_NAME, "wb")
      self._game_type_decisions_fh = open(Config.STORE_GAME_TYPE_DECISIONS_FILE_NAME, "wb")

    if Config.STORE_TRAINING_DATA and Config.ONLINE_TRAINING:
      training_description = "(training online AND storing data) "
    elif Config.STORE_TRAINING_DATA:
      training_description = "(storing training data) "
    elif Config.ONLINE_TRAINING:
      training_description = "(training online) "
    else:
      training_description = ""
    self.log.error("Starting game of {} hands: {} vs {} {}({} processes, {} batch size, {} rounds{})"
        .format(utils.format_human(Config.TOTAL_HANDS), Config.TEAM_1_STRATEGY, Config.TEAM_2_STRATEGY,
          training_description, Config.PARALLEL_PROCESSES,
          utils.format_human(Config.BATCH_SIZE), utils.format_human(Config.BATCH_COUNT),
          ", baseline: {}".format(Config.ENCODING.baseline) if Config.TEAM_1_STRATEGY == "baseline" or \
              Config.TEAM_2_STRATEGY == "baseline" else ""))
    if Config.FORCE_GAME_TYPE:
      self.log.warning("Forcing game type: {}".format(Config.FORCE_GAME_TYPE))
      assert self.players[0].knows_game_type(Config.FORCE_GAME_TYPE) and \
          self.players[1].knows_game_type(Config.FORCE_GAME_TYPE), "a team doesn't know the forced game type"
    else:
      assert self.players[0].knows_same_game_types_as(self.players[1]), "the teams don't know the same game types"

  def play(self):
    # pylint: disable=too-many-statements,too-many-branches
    self.initialize()

    start_time = time.time()
    played_hands = 0
    batch_round = 0
    parallel_games = [ParallelGame(self.players) for _ in range(Config.PARALLEL_PROCESSES)]
    last_to_index = 0

    if Config.STORE_TRAINING_DATA or Config.ONLINE_TRAINING:
      training_samples_per_batch = Const.DECISIONS_PER_HAND * Config.BATCH_SIZE
      training_samples_per_training = Const.DECISIONS_PER_HAND * Config.TRAINING_INTERVAL
      # setting it to ones immediately allocates space (which prevents surprises later on...)
      training_data = np.ones((training_samples_per_training, Const.CARDS_PER_HAND + 1), dtype=int)

    # retrieve processes
    results = [self.pool.apply_async(ParallelGame.set_seed_and_get_pid, (i+1,))
        for i in range(Config.PARALLEL_PROCESSES)]
    pool_pids = [result.get() for result in results]
    assert len(set(pool_pids)) == len(pool_pids)
    pids = [os.getpid()] + pool_pids
    self.log.info("Running with 1+{} processes: {}".format(len(pids)-1, " ".join(str(p) for p in pids)))
    processes = [Process(pid) for pid in pids]

    while played_hands < Config.TOTAL_HANDS:
      self.log.debug("Starting batch {}".format(batch_round+1))
      if Config.PARALLEL_PROCESSES > 1:
        batch = [self.pool.apply_async(game.play_hands, (played_hands + i * Config.BATCH_SIZE,))
          for i, game in enumerate(parallel_games)]
        self.log.debug("Started parallel batch of size {}".format(utils.format_human(Config.BATCH_SIZE)))
        results = [b.get() for b in batch]
      else:
        ParallelGame.inject_log(self.log) # this seems needed even though the pool is initialized with the log
        self.log.debug("Starting sequential batch of size {}".format(utils.format_human(Config.BATCH_SIZE)))
        results = [game.play_hands(played_hands + i * Config.BATCH_SIZE)
            for i, game in enumerate(parallel_games)]

      self.log.debug("Processing results of batch")
      for result in results:
        self._overall_score.add_other_score(result[0])
        self._selected_game_types += result[4]

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
          training_data[from_index:to_index] = result[1]
        if played_hands % Config.TRAINING_INTERVAL == 0:
          self._handle_training_data(training_data)

      # store game type decisions
      if Config.STORE_TRAINING_DATA:
        for result in results:
          self._write_game_type_decisions(result[2])

      # checkpoint
      if Config.STORE_SCORES:
        for result in results:
          self._checkpoint_data.extend(result[3])
      if played_hands % Config.CHECKPOINT_INTERVAL == 0:
        self._create_checkpoint(played_hands, Config.TOTAL_HANDS)
        if Config.STORE_SCORES:
          self._checkpoint_data.clear()

      # logging
      if played_hands % Config.LOGGING_INTERVAL == 0:
        memory = [round(process.memory_info().rss/1e6, 1) for process in processes]
        percentage = batch_round / Config.BATCH_COUNT

        elapsed_minutes = (time.time() - start_time) / 60
        estimated_hours, estimated_minutes = divmod(elapsed_minutes / percentage - elapsed_minutes, 60)
        self.log.warning(
            "Round {}/{} ({:.1f}%) ETA: {:%H:%M} ({}:{:02d}), {}/{} hands; current T1 wins: {:.1f}%, memory: {}={:.1f}M"
            .format(utils.format_human(batch_round), utils.format_human(Config.BATCH_COUNT), 100.0 * percentage,
              datetime.now() + timedelta(hours=estimated_hours, minutes=estimated_minutes),
              int(estimated_hours), int(estimated_minutes),
              utils.format_human(played_hands), utils.format_human(Config.TOTAL_HANDS),
              self._overall_score.team_1_win_percentage, "+".join(str(m) for m in memory), sum(memory)))

    # the game is over
    self._print_results()

    # cleanup
    if self._training_data_fh:
      self._training_data_fh.close()
    if self._game_type_decisions_fh:
      self._game_type_decisions_fh.close()
    if self._score_fh:
      self._score_fh.close()

  def _handle_training_data(self, training_data):
    if Config.STORE_TRAINING_DATA:
      self._write_training_data(training_data)
    if Config.ONLINE_TRAINING:
      for player in self._get_distinct_strategy_players():
        player.train(training_data, self.log)

  def _write_game_type_decisions(self, game_type_decisions):
    self._game_type_decisions_fh.write(struct.pack(
      "=" + ("B{}h".format(Const.CARDS_PER_PLAYER * "B")) * len(game_type_decisions),
      *game_type_decisions.reshape(-1)))

  def _create_checkpoint(self, current_iteration, total_iterations):
    if Config.STORE_SCORES:
      self.log.debug("Writing {} scores at iteration {}/{} ({:.1f}%)"
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

  def _write_scores_header(self):
    header = "hand,wins_team_1,score_team_1,wins_team_2,score_team_2,team_1_info,team_2_info\n"
    self._score_fh.write(header)

  def _write_training_data(self, training_data):
    self.log.info("Writing {} training samples to {}".format(
      utils.format_human(len(training_data)), self._training_data_fh.name))

    # write each sample separately - not optimal for disk but avoids copying memory
    for sample in training_data:
      self._training_data_fh.write(struct.pack("=" + ("{}h".format(Const.CARDS_PER_HAND * "B")), *sample))

  def _print_results(self):
    # set up result message
    score_of_both_teams = self._overall_score.total_score_team_1 + self._overall_score.total_score_team_2
    message = "Overall result: {} ({}) vs {} ({}){}; wins: {} vs {}; " + \
        "(score diff {}, off mean: {:.2f}%, T1 win percentage: {:.2f}%)"
    formatted_message = message.format(
      utils.format_human(self._overall_score.total_score_team_1), Config.TEAM_1_STRATEGY,
      utils.format_human(self._overall_score.total_score_team_2), Config.TEAM_2_STRATEGY,
      ", baseline: {}".format(Config.ENCODING.baseline) if Config.TEAM_1_STRATEGY == "baseline" or \
          Config.TEAM_2_STRATEGY == "baseline" else "",
      utils.format_human(self._overall_score.wins_team_1), utils.format_human(self._overall_score.wins_team_2),
      utils.format_human(int((self._overall_score.total_score_team_1*2-score_of_both_teams)/2)),
      100.0*(self._overall_score.total_score_team_1*2-score_of_both_teams)/2/score_of_both_teams,
      self._overall_score.team_1_win_percentage)

    # actually log result message
    if self._overall_score.team_1_win_percentage < 70 and self._overall_score.team_1_win_percentage > 50:
      self.log.warning(formatted_message)
    else:
      utils.log_success_or_error(self.log, self._overall_score.wins_team_1 > self._overall_score.wins_team_2,
          formatted_message)

    # game type selections
    selected_percentages = self._selected_game_types / self._selected_game_types.sum(axis=1, keepdims=True)
    self.log.info("Selected game types per player: {} {}, {} {}; {} {}, {} {}".format(
      self.players[0].name, selected_percentages[0], self.players[2].name, selected_percentages[2],
      self.players[1].name, selected_percentages[1], self.players[3].name, selected_percentages[3]))
