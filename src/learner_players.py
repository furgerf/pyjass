#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import os
import pickle
import time
from config import Config
from datetime import datetime, timedelta

import numpy as np

import utils
from const import Const
from player import Player
from sklearn.linear_model import SGDRegressor
from sklearn.neural_network import MLPRegressor


class LearnerPlayer(Player):
  """
  Base class of ML-based players.
  """

  def __init__(self, name, number, play_best_card, regressor, log):
    """
    Creates a new ML-based player.

    :name: Name of the player, for display purposes only.
    :number: Number of the player, to determine neighboring players.
    :play_best_card: True if the player should always play the card he thinks is best, may be ignored.
    :regressor: Model to use.
    :log: Logger instance.
    """
    self.regressor = regressor
    self.last_training_done = time.time()
    super(LearnerPlayer, self).__init__(name, number, play_best_card, log)

  @staticmethod
  def _get_regressor(regressor_constructor, log, regressor_name=None):
    """
    Retrieves the model. Either loads an existing or creates a new model.
    Also does initial offline training so that the returned model is always valid and ready for inference.

    :regressor_constructor: Constructor to instantiate a new model.
    :log: Logger instance.
    :regressor_name: Optional: Name of the model to load.

    :returns: Model instance.
    """
    # TODO: Simplify
    # ensure there's a loss file with the expected header
    if Config.ONLINE_TRAINING and not os.path.exists(Config.LOSS_FILE):
      with open(Config.LOSS_FILE, "w") as fh:
        fh.write("samples,loss\n")

    pickle_file_name = "{}/{}".format(Config.MODEL_DIRECTORY, regressor_name or Config.REGRESSOR_NAME)
    if os.path.exists(pickle_file_name):
      with open(pickle_file_name, "rb") as fh:
        regressor = pickle.load(fh)
        real_path = os.path.realpath(pickle_file_name)[len(os.getcwd())+1:]
        path_difference = "" if real_path == pickle_file_name else " ({})".format(real_path)
        log.info("Loaded model from {}{} (trained on {} samples - {} hands, loss {:.1f})".format(pickle_file_name,
          path_difference, utils.format_human(regressor.training_samples),
          utils.format_human(regressor.training_samples/32), regressor.loss_))
        assert regressor.__class__.__name__ == regressor_constructor.__name__, \
            "Loaded model is a different type than desired, aborting"

        if Config.ONLINE_TRAINING:
          # this is a bit of a crutch to avoid writing the loss when creating the LC...
          with open(Config.LOSS_FILE, "a") as fh:
            fh.write("{},{}\n".format(regressor.training_samples, regressor.loss_))

        if Config.LOAD_TRAINING_DATA_FILE_NAME and os.path.exists(Config.LOAD_TRAINING_DATA_FILE_NAME):
          log.warning("Training loaded model on stored data: {}".format(Config.LOAD_TRAINING_DATA_FILE_NAME))
          log.info("Model details: {}".format(regressor))
          LearnerPlayer._train_regressor_from_file(regressor, log)

          trained_pickle_file_name = "{}/{}-trained-offline.pkl".format(Config.EVALUATION_DIRECTORY,
              os.path.splitext(Config.REGRESSOR_NAME)[0])
          log.warning("Writing newly-trained model to {}".format(trained_pickle_file_name))
          with open(trained_pickle_file_name, "wb") as fh:
            pickle.dump(regressor, fh)
        else:
          log.info("Model details: {}".format(regressor))
        return regressor

    assert Config.LOAD_TRAINING_DATA_FILE_NAME and os.path.exists(Config.LOAD_TRAINING_DATA_FILE_NAME), \
        "Found neither regressor '{}' nor training data file '{}'".format(
            Config.REGRESSOR_NAME, Config.LOAD_TRAINING_DATA_FILE_NAME)

    regressor_args = Config.TEAM_1_MODEL_ARGS or {}
    if regressor_args:
      log.warning("Applying custom arguments: '{}'".format(regressor_args))
    regressor_args["warm_start"] = True
    regressor = regressor_constructor(**regressor_args)
    regressor.training_samples = 0

    log.warning("Training new model on stored data {}: {}".format(Config.LOAD_TRAINING_DATA_FILE_NAME, regressor))
    LearnerPlayer._train_regressor_from_file(regressor, log)
    log.warning("Writing newly-trained model to {}".format(pickle_file_name))
    with open(pickle_file_name, "wb") as fh:
      pickle.dump(regressor, fh)

    return regressor

  @staticmethod
  def _train_regressor_from_file(regressor, log):
    """
    Trains the provided regressor on offline data.

    :regressor: Model instance.
    :log: Logger instance.
    """
    # TODO: Simplify
    offset = 0
    training_start = time.time()
    if Config.LOAD_TRAINING_DATA_FILE_NAME.endswith("csv"):
      iterator = iter(utils.process_csv_file(Config.LOAD_TRAINING_DATA_FILE_NAME))
      log.info("Skipping header '{}'".format(next(iterator)))
      for chunk in utils.batch(iterator, Const.OFFLINE_CHUNK_SIZE):
        training_data = np.array(list(chunk), dtype=int)
        offset += len(training_data)
        log.debug("Loaded {} lines from {} ({} lines done)".format(
          utils.format_human(len(training_data)), Config.LOAD_TRAINING_DATA_FILE_NAME, utils.format_human(offset)))
        LearnerPlayer._train_regressor(regressor, training_data, log)
    else:
      total_samples = os.stat(Config.LOAD_TRAINING_DATA_FILE_NAME).st_size / Const.BYTES_PER_SAMPLE
      for training_data in utils.process_binary_file(Config.LOAD_TRAINING_DATA_FILE_NAME, Const.OFFLINE_CHUNK_SIZE):
        offset += len(training_data)
        log.debug("Loaded {} samples from {} ({} samples done)".format(
          utils.format_human(len(training_data)), Config.LOAD_TRAINING_DATA_FILE_NAME, utils.format_human(offset)))
        LearnerPlayer._train_regressor(regressor, training_data, log)
        if offset % (Const.OFFLINE_CHUNK_SIZE * 5) == 0:
          percentage = offset / total_samples
          elapsed_minutes = (time.time() - training_start) / 60
          estimated_hours, estimated_minutes = divmod(elapsed_minutes / percentage - elapsed_minutes, 60)
          log.warning("Processed {}/{} ({:.1f}%) samples from '{}', ETA: {:%H:%M} ({}:{:02d})".format(
            utils.format_human(offset), utils.format_human(total_samples), 100.0*percentage,
            Config.LOAD_TRAINING_DATA_FILE_NAME,
            datetime.now() + timedelta(hours=estimated_hours, minutes=estimated_minutes),
            int(estimated_hours), int(estimated_minutes)
            ))
    training_hours, training_minutes = divmod((time.time() - training_start)/60, 60)
    log.warning("Finished offline training in {}h{}m".format(int(training_hours), int(training_minutes)))

  def _select_card(self, args, log):
    valid_cards, played_cards, known_cards = args
    state = self._encode_current_state(played_cards, known_cards)
    states = []
    scores = []
    for card in valid_cards:
      my_state = np.array(state, copy=True)
      my_state[card.card_index] = Config.ENCODING.card_code_selected
      if Config.ENCODING.sort_states:
        my_state = Player._sort_decision_state(my_state)
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
    """
    Trains the provided model on the provided training data.

    :regressor: Model to train.
    :training_data: 2D-numpy-array of samples to train on.
    :log: Logger instance.
    :last_training_done: Optional. Time when the last training was done.
    """
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
    log.info("Trained {} on {} new samples (now has {} - {} hands) in {}m{}s{}; loss {:.1f}".format(
      regressor.__class__.__name__, utils.format_human(len(training_data)),
      utils.format_human(regressor.training_samples),
      utils.format_human(regressor.training_samples/Const.DECISIONS_PER_HAND),
      int(training_mins), int(training_secs), since_last, regressor.loss_))

  def checkpoint(self, current_iteration, total_iterations, log):
    unformatted_file_name = "{}_{}_{:0" + str(int(math.log10(total_iterations))+1) + "d}.pkl"
    file_name = unformatted_file_name.format(self.name,
        self.regressor.__class__.__name__, current_iteration)
    file_path = "{}/{}".format(Config.EVALUATION_DIRECTORY, file_name)
    log.info("Storing model in '{}' at iteration {}/{} ({:.1f}%)".format(file_name,
      utils.format_human(current_iteration), utils.format_human(total_iterations),
      100.0*current_iteration/total_iterations))

    with open(file_path, "wb") as fh:
      pickle.dump(self.regressor, fh)

  def get_checkpoint_data(self):
    return self.regressor.training_samples


class SgdPlayer(LearnerPlayer):
  """
  ML-player using a Stochastic Gradient Descent model.
  """

  _sgd_regressor = None

  def __init__(self, name, number, play_best_card, log):
    if SgdPlayer._sgd_regressor is None:
      SgdPlayer._sgd_regressor = LearnerPlayer._get_regressor(SGDRegressor, log)
    super(SgdPlayer, self).__init__(name, number, play_best_card, SgdPlayer._sgd_regressor, log)


class MlpPlayer(LearnerPlayer):
  """
  ML-player using a Multilayer Perceptron model.
  """

  _mlp_regressor = None

  def __init__(self, name, number, play_best_card, log):
    if MlpPlayer._mlp_regressor is None:
      MlpPlayer._mlp_regressor = LearnerPlayer._get_regressor(MLPRegressor, log)
    super(MlpPlayer, self).__init__(name, number, play_best_card, MlpPlayer._mlp_regressor, log)


class OtherMlpPlayer(LearnerPlayer):
  """
  Another ML-player using a Multilayer Perceptron model.
  """

  _mlp_regressor = None

  def __init__(self, name, number, play_best_card, log):
    if OtherMlpPlayer._mlp_regressor is None:
      log.fatal("WARNING: If the other model is trained on an incompatible encoding, it probably won't work!")
      OtherMlpPlayer._mlp_regressor = LearnerPlayer._get_regressor(MLPRegressor, log,
          regressor_name=Config.OTHER_REGRESSOR_NAME)
    super(OtherMlpPlayer, self).__init__(name, number, play_best_card, OtherMlpPlayer._mlp_regressor, log)
