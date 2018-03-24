#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import os
import pickle
import time

import numpy as np
import utils
from config import Config
from player import Player
from sklearn.linear_model import SGDRegressor
from sklearn.neural_network import MLPRegressor


class LearnerPlayer(Player):
  def __init__(self, name, play_best_card, regressor, log):
    self.regressor = regressor
    self.last_training_done = time.time()

    super(LearnerPlayer, self).__init__(name, play_best_card, log)

  @staticmethod
  def _get_regressor(regressor_constructor, log):
    if Config.ONLINE_TRAINING:
      if not os.path.exists(Config.LOSS_FILE):
        with open(Config.LOSS_FILE, "w") as fh:
          fh.write("samples,loss\n")

    pickle_file_name = "{}/{}".format(Config.MODEL_DIRECTORY, Config.REGRESSOR_NAME)
    if os.path.exists(pickle_file_name):
      with open(pickle_file_name, "rb") as fh:
        regressor = pickle.load(fh)
        real_path = os.path.realpath(pickle_file_name)[len(os.getcwd())+1:]
        path_difference = "" if real_path == pickle_file_name else " ({})".format(real_path)
        log.error("Loaded model from {}{} (trained on {} samples)".format(pickle_file_name,
          path_difference, utils.format_human(regressor.training_samples)))
        assert regressor.__class__.__name__ == regressor_constructor.__name__, \
            "Loaded model is a different type than desired, aborting"

        if Config.ONLINE_TRAINING:
          # this is a bit of a crutch to avoid writing the loss when creating the LC...
          with open(Config.LOSS_FILE, "a") as fh:
            fh.write("{},{}\n".format(regressor.training_samples, regressor.loss_))

        if Config.ONLINE_TRAINING and Config.TRAINING_DATA_FILE_NAME:
          log.info("Training loaded model on stored data {}: {}".format(Config.TRAINING_DATA_FILE_NAME, regressor))
          LearnerPlayer._train_regressor_from_file(regressor, log)

          trained_pickle_file_name = "{}/{}-trained-offline".format(Config.EVALUATION_DIRECTORY, Config.REGRESSOR_NAME)
          log.warning("Writing newly-trained model to {}".format(trained_pickle_file_name))
          with open(trained_pickle_file_name, "wb") as fh:
            pickle.dump(regressor, fh)
        else:
          log.info("Model details: {}".format(regressor))
        return regressor

    assert Config.ONLINE_TRAINING, "Must do online training when starting with a model from scratch"

    assert Config.TRAINING_DATA_FILE_NAME and os.path.exists(Config.TRAINING_DATA_FILE_NAME), \
        "Found neither regressor '{}' nor training data file '{}'".format(
            Config.REGRESSOR_NAME, Config.TRAINING_DATA_FILE_NAME)

    regressor_args = Config.TEAM_1_MODEL_ARGS or {}
    if regressor_args:
      log.warning("Applying custom arguments: '{}'".format(regressor_args))
    regressor_args["warm_start"] = True
    regressor = regressor_constructor(**regressor_args)
    regressor.training_samples = 0

    log.info("Training new model on stored data {}: {}".format(Config.TRAINING_DATA_FILE_NAME, regressor))
    LearnerPlayer._train_regressor_from_file(regressor, log)
    log.warning("Writing newly-trained model to {}".format(pickle_file_name))
    with open(pickle_file_name, "wb") as fh:
      pickle.dump(regressor, fh)

    return regressor

  @staticmethod
  def _train_regressor_from_file(regressor, log):
    offset = 0
    chunk_size = int(1.6e6)

    if Config.TRAINING_DATA_FILE_NAME.endswith("csv"):
      iterator = iter(utils.process_csv_file(Config.TRAINING_DATA_FILE_NAME))
      log.info("Skipping header '{}'".format(next(iterator)))
      for chunk in utils.batch(iterator, chunk_size):
        training_data = np.array(list(chunk), dtype=int)
        offset += len(training_data)
        log.debug("Loaded {} lines from {} ({} lines done)".format(
          utils.format_human(len(training_data)), Config.TRAINING_DATA_FILE_NAME, utils.format_human(offset)))
        LearnerPlayer._train_regressor(regressor, training_data, log)
    else:
      for training_data in utils.process_binary_file(Config.TRAINING_DATA_FILE_NAME, chunk_size):
        offset += len(training_data)
        log.debug("Loaded {} samples from {} ({} samples done)".format(
          utils.format_human(len(training_data)), Config.TRAINING_DATA_FILE_NAME, utils.format_human(offset)))
        LearnerPlayer._train_regressor(regressor, training_data, log)

  def _select_card(self, args, log):
    valid_cards, played_cards, known_cards = args
    state = self._encode_cards(played_cards, known_cards)
    states = []
    scores = []
    for card in valid_cards:
      my_state = np.array(state, copy=True)
      my_state[card.card_index] = Config.ENCODING.card_code_selected
      states.append(my_state)

    if len(valid_cards) == 1:
      log.debug("Selecting the only valid card {}".format(valid_cards[0]))
      return valid_cards[0]
    scores = self.regressor.predict(states)
    if self._play_best_card:
      card = valid_cards[np.argmax(scores)]
    else:
      if np.min(scores) < 0:
        adjusted_scores = scores - np.min(scores)
        score_sum = np.sum(adjusted_scores)
        if score_sum == 0:
          score_sum += 1
        probabilities = adjusted_scores / score_sum
        log.debug("Using adjusted scores {} instead of normal scores {} with probabilities {}"
            .format(adjusted_scores, scores, probabilities))
      else:
        score_sum = np.sum(scores)
        if score_sum == 0:
          score_sum += 1
        probabilities = scores / score_sum
      card = valid_cards[np.random.choice(len(probabilities), p=probabilities)]
    log.debug("Playing cards {} has predicted scores of {}, selecting {}"
        .format(utils.format_cards(valid_cards), scores, card))
    return card

  def train(self, training_data, log):
    LearnerPlayer._train_regressor(self.regressor, training_data, log, self.last_training_done)
    self.last_training_done = time.time()

  @staticmethod
  def _train_regressor(regressor, training_data, log, last_training_done=None):
    training_start = time.time()
    regressor.partial_fit(training_data[:, :-1], training_data[:, -1])
    regressor.training_samples += len(training_data)

    with open(Config.LOSS_FILE, "a") as fh:
      fh.write("{},{}\n".format(regressor.training_samples, regressor.loss_))

    training_mins, training_secs = divmod(time.time() - training_start, 60)
    since_last = ""
    if last_training_done:
      last_mins, last_secs = divmod(time.time() - last_training_done, 60)
      since_last = " ({}m{}s since last)".format(int(last_mins), int(last_secs))
    log.info("Trained {} on {} new samples (now has {}) in {}m{}s{}; loss {:.1f}".format(
      regressor.__class__.__name__, utils.format_human(len(training_data)),
      utils.format_human(regressor.training_samples),
      int(training_mins), int(training_secs), since_last, regressor.loss_))

  def checkpoint(self, current_iteration, total_iterations, log):
    unformatted_file_name = "{}_{}_{:0" + str(int(math.log10(total_iterations))+1) + "d}.pkl"
    file_name = unformatted_file_name.format(self.name,
        self.regressor.__class__.__name__, current_iteration)
    file_path = "{}/{}".format(Config.EVALUATION_DIRECTORY, file_name)
    log.warning("Storing model in '{}' at iteration {}/{} ({:.1f}%)".format(file_name,
      utils.format_human(current_iteration), utils.format_human(total_iterations),
      100.0*current_iteration/total_iterations))

    with open(file_path, "wb") as fh:
      pickle.dump(self.regressor, fh)

  def get_checkpoint_data(self):
    return self.regressor.training_samples


class SgdPlayer(LearnerPlayer):
  _sgd_regressor = None

  def __init__(self, name, play_best_card, log):
    if SgdPlayer._sgd_regressor is None:
      SgdPlayer._sgd_regressor = LearnerPlayer._get_regressor(SGDRegressor, log)
    super(SgdPlayer, self).__init__(name, play_best_card, SgdPlayer._sgd_regressor, log)


class MlpPlayer(LearnerPlayer):
  _mlp_regressor = None

  def __init__(self, name, play_best_card, log):
    if MlpPlayer._mlp_regressor is None:
      MlpPlayer._mlp_regressor = LearnerPlayer._get_regressor(MLPRegressor, log)
    super(MlpPlayer, self).__init__(name, play_best_card, MlpPlayer._mlp_regressor, log)
