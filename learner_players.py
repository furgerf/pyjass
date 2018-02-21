#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pickle
from config import Config
from os import path

import numpy as np

import utils
from card import Card
from player import Player
from sklearn.linear_model import SGDRegressor
from sklearn.neural_network import MLPRegressor


class LearnerPlayer(Player):
  def __init__(self, name, regressor, log):
    self.regressor = regressor
    super(LearnerPlayer, self).__init__(name, log)

  def _get_regressor(self, pickle_file_name, regressor_constructor, regressor_args):
    if path.exists(pickle_file_name):
      with open(pickle_file_name, "rb") as fh:
        self.log.warning("Loading model from {}".format(pickle_file_name))
        return pickle.load(fh)

    regressor = regressor_constructor(**regressor_args)
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

      offset += chunk_size
      self.log.info("Fitting regressor with {} samples".format(utils.format_human(len(training_data))))
      regressor.partial_fit(training_data[:, :-1], training_data[:, -1])

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
      my_state[card.card_index] = Card.SELECTED
      states.append(my_state)

    scores = self.regressor.predict(states)
    # TODO: Select according to probability relative to score
    card = valid_cards[np.argmax(scores)]
    self.log.debug("Playing cards {} has predicted score of {}, selecting {}"
        .format(utils.format_cards(valid_cards), scores, card))
    return card


class SgdPlayer(LearnerPlayer):
  _sgd_regressor = None

  def __init__(self, name, log):
    self.log = log
    if SgdPlayer._sgd_regressor is None:
      SgdPlayer._sgd_regressor = self._get_regressor(
          "{}/sgd-model.pkl".format(Config.MODEL_DIRECTORY), SGDRegressor, {
            "warm_start": True
            })

    super(SgdPlayer, self).__init__(name, SgdPlayer._sgd_regressor, log)


class MlpPlayer(LearnerPlayer):
  _mlp_regressor = None

  def __init__(self, name, log):
    self.log = log
    if MlpPlayer._mlp_regressor is None:
      MlpPlayer._mlp_regressor = self._get_regressor(
          "{}/mlp-model.pkl".format(Config.MODEL_DIRECTORY), MLPRegressor, {
            "warm_start": True
            })

    super(MlpPlayer, self).__init__(name, MlpPlayer._mlp_regressor, log)
