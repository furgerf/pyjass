#!/usr/bin/env python
# -*- coding: utf-8 -*-


import math
import pickle
from config import Config
from os import path

import numpy as np

import utils
from player import Player
from sklearn.linear_model import SGDRegressor
from sklearn.neural_network import MLPRegressor


class LearnerPlayer(Player):
  def __init__(self, name, play_best_card, regressor, log):
    self.regressor = regressor
    super(LearnerPlayer, self).__init__(name, play_best_card, log)

  def _get_regressor(self, pickle_file_name, regressor_constructor, regressor_args):
    if path.exists(pickle_file_name):
      with open(pickle_file_name, "rb") as fh:
        self.log.warning("Loading model from {}".format(pickle_file_name))
        return pickle.load(fh)

    regressor = regressor_constructor(**regressor_args)
    regressor.training_samples = 0
    self.log.info("Training model: {}".format(regressor))
    offset = 0
    chunk_size = int(1e6)
    while True:
      self.log.info("Loading data from {} ({} lines done)".format(
        Config.TRAINING_DATA_FILE_NAME, utils.format_human(offset)))
      training_data = np.genfromtxt(Config.TRAINING_DATA_FILE_NAME,
          delimiter=",", dtype=int, skip_header=1+offset, max_rows=chunk_size)

      if not training_data.any():
        self.log.warning("Finished training model: {}".format(regressor))
        break

      self.log.info("Fitting regressor with {} samples".format(utils.format_human(len(training_data))))
      regressor.partial_fit(training_data[:, :-1], training_data[:, -1])
      offset += len(training_data)
      regressor.training_samples += len(training_data)

    self.log.warning("Writing newly-trained model to {}".format(pickle_file_name))
    with open(pickle_file_name, "wb") as fh:
      pickle.dump(regressor, fh)
    return regressor

  def _select_card(self, args):
    valid_cards, played_cards, known_cards = args
    state = self._encode_cards(played_cards, known_cards)
    states = []
    scores = []
    for card in valid_cards:
      my_state = np.array(state, copy=True)
      my_state[card.card_index] = Config.ENCODING.card_code_selected
      states.append(my_state)

    scores = self.regressor.predict(states)
    if self._play_best_card:
      card = valid_cards[np.argmax(scores)]
    else:
      if np.min(scores) < 0:
        adjusted_scores = scores - np.min(scores)
        probabilities = adjusted_scores / np.sum(adjusted_scores)
        self.log.warning("Using adjusted scores {} instead of normal scores {} with probabilities {}"
            .format(adjusted_scores, scores, probabilities))
      else:
        probabilities = scores / np.sum(scores)
      card = valid_cards[np.random.choice(len(probabilities), p=probabilities)]
    self.log.debug("Playing cards {} has predicted scores of {}, selecting {}"
        .format(utils.format_cards(valid_cards), scores, card))
    return card

  def train(self, training_data):
    self.log.debug("Training player {} with {} new samples".format(self._name, len(training_data)))
    data = np.array(training_data)
    self.regressor.partial_fit(data[:, :-1], data[:, -1])
    self.regressor.training_samples += len(training_data)

  def checkpoint(self, current_iteration, total_iterations):
    unformatted_file_name = "{}/{}_{}_{:0" + str(int(math.log10(total_iterations))+1) + "d}.pkl"
    file_name = unformatted_file_name.format(Config.EVALUATION_DIRECTORY, self.name,
        self.regressor.__class__.__name__, current_iteration)
    with open(file_name, "wb") as fh:
      pickle.dump(self.regressor, fh)

  def get_checkpoint_data(self):
    return self.regressor.training_samples


class SgdPlayer(LearnerPlayer):
  _sgd_regressor = None

  def __init__(self, name, play_best_card, log):
    self.log = log
    if SgdPlayer._sgd_regressor is None:
      SgdPlayer._sgd_regressor = self._get_regressor(
          "{}/sgd-model.pkl".format(Config.MODEL_DIRECTORY), SGDRegressor, {
            "warm_start": True
            })

    super(SgdPlayer, self).__init__(name, play_best_card, SgdPlayer._sgd_regressor, log)


class MlpPlayer(LearnerPlayer):
  _mlp_regressor = None

  def __init__(self, name, play_best_card, log):
    self.log = log
    if MlpPlayer._mlp_regressor is None:
      MlpPlayer._mlp_regressor = self._get_regressor(
          "{}/mlp-model.pkl".format(Config.MODEL_DIRECTORY), MLPRegressor, {
            "warm_start": True
            })

    super(MlpPlayer, self).__init__(name, play_best_card, MlpPlayer._mlp_regressor, log)
