#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from abc import abstractmethod, abstractproperty
from datetime import datetime, timedelta

import numpy as np

import utils
from config import Config
from const import Const
from player import Player


class LearnerPlayer(Player):
  """
  Base class of ML-based players. Currently, any ML player is only for a specific game type.
  """

  def __init__(self, name, number, known_game_types, log):
    """
    Creates a new ML-based player.

    :name: Name of the player, for display purposes only.
    :number: Number of the player, to determine neighboring players.
    :known_game_types: A list of the known game types of the player.
    :log: Logger instance.
    """
    self.last_training_done = time.time()
    super(LearnerPlayer, self).__init__(name, number, known_game_types, log)

  @abstractproperty
  def trained_samples(self):
    """
    Returns the number of samples the model has been trained on.
    """
    pass

  @abstractproperty
  def model_type(self):
    """
    Returns a description of the model type.
    """
    pass

  @abstractmethod
  def _train_model(self, training_data, log):
    """
    Trains the model on the provided training data.

    :training_data: 2D-numpy-array of samples to train on.
    :log: Logger instance. UNUSED?

    :returns: Current loss of the model.
    """
    pass

  @abstractmethod
  def _predict_scores(self, states):
    """
    Returns the predicted scores of the provided states.

    :states: The states to predict scores for.

    :returns: The scores for the states.
    """
    pass

  def train(self, training_data, log):
    training_start = time.time()

    loss = self._train_model(training_data, log)

    with open(Config.LOSS_FILE, "a") as fh:
      fh.write("{},{}\n".format(self.trained_samples, loss))

    training_mins, training_secs = divmod(time.time() - training_start, 60)
    since_last = ""
    if self.last_training_done:
      last_mins, last_secs = divmod(time.time() - self.last_training_done, 60)
      since_last = " ({}m{}s since last)".format(int(last_mins), int(last_secs))
    log.info("Trained {} on {} new hands (now has {}) in {}m{}s{}; loss {:.1f}".format(
      self.model_type, utils.format_human(len(training_data)/Const.DECISIONS_PER_HAND),
      utils.format_human(self.trained_samples/Const.DECISIONS_PER_HAND),
      int(training_mins), int(training_secs), since_last, loss))

    self.last_training_done = time.time()

  def _train_regressor_from_file(self, log):
    """
    Trains on offline data.

    :log: Logger instance.
    """
    offset = 0
    training_start = time.time()
    total_hands = os.stat(Config.LOAD_TRAINING_DATA_FILE_NAME).st_size/Const.BYTES_PER_SAMPLE/Const.DECISIONS_PER_HAND
    log.warning("Training regressor with {} hands on {} new hands from file {}".format(
      utils.format_human(self.trained_samples/Const.DECISIONS_PER_HAND),
      utils.format_human(total_hands), Config.LOAD_TRAINING_DATA_FILE_NAME))
    for training_data in utils.process_binary_file(Config.LOAD_TRAINING_DATA_FILE_NAME, Const.OFFLINE_CHUNK_SIZE):
      offset += len(training_data)
      log.debug("Loaded {} hands from {} ({} hands done)".format(
        utils.format_human(len(training_data)/Const.DECISIONS_PER_HAND),
        Config.LOAD_TRAINING_DATA_FILE_NAME, utils.format_human(offset/Const.DECISIONS_PER_HAND)))

      self.train(training_data, log)

      if offset % (Const.OFFLINE_CHUNK_SIZE * 5) == 0:
        percentage = offset / Const.DECISIONS_PER_HAND / total_hands
        elapsed_minutes = (time.time() - training_start) / 60
        estimated_hours, estimated_minutes = divmod(elapsed_minutes / percentage - elapsed_minutes, 60)
        log.warning("Processed {}/{} ({:.1f}%) hands from '{}', ETA: {:%H:%M} ({}:{:02d})".format(
          utils.format_human(offset/Const.DECISIONS_PER_HAND), utils.format_human(total_hands), 100.0*percentage,
          Config.LOAD_TRAINING_DATA_FILE_NAME,
          datetime.now() + timedelta(hours=estimated_hours, minutes=estimated_minutes),
          int(estimated_hours), int(estimated_minutes)
          ))
    training_hours, training_minutes = divmod((time.time() - training_start)/60, 60)
    log.warning("Finished offline training in {}h{}m".format(int(training_hours), int(training_minutes)))

  def get_checkpoint_data(self):
    return self.trained_samples

  def _select_card(self, args, log):
    valid_cards, played_cards, known_cards, _ = args
    states = []
    scores = []

    state = self._encode_current_state(played_cards, known_cards)
    for card in valid_cards:
      my_state = np.array(state, copy=True)
      my_state[card.card_index] = Config.ENCODING.card_code_selected + \
          (Config.ENCODING.trump_code_offset if card.is_trump else 0)
      if Config.ENCODING.sort_states:
        my_state = Player._sort_decision_state(my_state, Config.ENCODING.card_index_by_suit)
      states.append(my_state)

    if len(valid_cards) == 1:
      log.debug("Selecting the only valid card {}".format(valid_cards[0]))
      return valid_cards[0]
    scores = self._predict_scores(states)
    card = valid_cards[np.argmax(scores)]
    log.debug("Playing cards {} has predicted scores of {}, selecting {}"
        .format(utils.format_cards(valid_cards), scores, card))
    return card

  def _select_game_type(self):
    raise RuntimeError("Learner players shouldn't be asked to select a game type")
