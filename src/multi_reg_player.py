#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pickle
from config import Config

import numpy as np

import utils
from player import Player


class MultiRegPlayer(Player):
  """
  A player which consists of multiple regressors, one for game type selection and the others for
  the different game types.

  Note that this player uses ML models but isn't trained directly itself.
  """

  def __init__(self, name, number, log):
    """
    Creates a new multi-regressor player.

    :name: Name of the player, for display purposes only.
    :number: Number of the player, to determine neighboring players.
    :log: Logger instance.
    """
    self.regressors = MultiRegPlayer._load_regressors(log)
    super(MultiRegPlayer, self).__init__(name, number, log)

  @staticmethod
  def _load_regressors(log):
    pickle_file_name = "{}/{}".format(Config.MODEL_DIRECTORY, Config.REGRESSOR_NAME)
    if not os.path.exists(pickle_file_name):
      raise RuntimeError("Regressor file '{}' doesn't exist")

    with open(pickle_file_name, "rb") as fh:
      regressors = pickle.load(fh)
    assert isinstance(regressors, dict), "The regressors should map regressors to game types"
    real_path = os.path.realpath(pickle_file_name)[len(os.getcwd())+1:]
    path_difference = "" if real_path == pickle_file_name else " ({})".format(real_path)
    log.info("Loaded regressors from {}{}".format(pickle_file_name, path_difference))
    for game_type, regressor in regressors.items():
      log.info("{}: {}, trained on {} samples - {} hands, loss {:.1f}".format(game_type,
        regressor.__class__.__name__, utils.format_human(regressor.training_samples),
        utils.format_human(regressor.training_samples/32), regressor.loss_))

    return regressors

  def _select_card(self, args, log):
    valid_cards, played_cards, known_cards, game_type = args
    regressor = self.regressors.get(game_type)
    if not regressor:
      raise RuntimeError("Don't have a regressor for game type '{}'".format(game_type))

    states = []
    scores = []

    state = self._encode_current_state(played_cards, known_cards)
    for card in valid_cards:
      my_state = np.array(state, copy=True)
      my_state[card.card_index] = Config.ENCODING.card_code_selected
      if Config.ENCODING.sort_states:
        my_state = Player._sort_decision_state(my_state)
      states.append(my_state)

    if len(valid_cards) == 1:
      log.debug("Selecting the only valid card {}".format(valid_cards[0]))
      return valid_cards[0]
    scores = regressor.predict(states)
    card = valid_cards[np.argmax(scores)]
    log.debug("Playing cards {} has predicted scores of {}, selecting {}"
        .format(utils.format_cards(valid_cards), scores, card))
    return card

  def _select_game_type(self):
    raise NotImplementedError()

  def train(self, training_data, log):
    raise RuntimeError("MultiReg players shouldn't be trained")

  def checkpoint(self, current_iteration, total_iterations, log):
    raise RuntimeError("MultiReg players shouldn't be checkpointed")

  def get_checkpoint_data(self):
    raise RuntimeError("MultiReg players shouldn't be checkpointed")
