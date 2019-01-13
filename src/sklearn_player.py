#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import os
import pickle
import time

from sklearn.linear_model import SGDRegressor
from sklearn.neural_network import MLPRegressor

import utils
from config import Config
from const import Const
from learner_player import LearnerPlayer


class SklearnPlayer(LearnerPlayer):
  """
  A learner player based on sklearn.
  """

  def __init__(self, name, number, regressor, offline_training, log, regressor_name=None):
    """
    Creates a new sklearn-based player.

    :name: Name of the player, for display purposes only.
    :number: Number of the player, to determine neighboring players.
    :regressor: Regressor model to use.
    :offline_training: True if the model should be trained offline.
    :log: Logger instance.
    :regressor_name: Optional: Name of the regressor. Uses the config's name if not specified.
    """
    self.regressor = regressor
    self.last_training_done = time.time()

    if offline_training:
      # need to define the file name before training (to determine if it's a new model)
      new_model_file_name = "{}/{}".format(Config.MODEL_DIRECTORY, regressor_name or Config.REGRESSOR_NAME)
      existing_model_file_name = "{}/{}-trained-offline.pkl".format(Config.EVALUATION_DIRECTORY,
          os.path.splitext(regressor_name or Config.REGRESSOR_NAME)[0])
      trained_model_file = existing_model_file_name if self.trained_samples else new_model_file_name
      self._train_regressor_from_file(log)
      log.info("Writing newly-trained regressor to {}".format(trained_model_file))
      with open(trained_model_file, "wb") as fh:
        pickle.dump(regressor, fh)

    super(SklearnPlayer, self).__init__(name, number, [self.regressor.game_type], log)

  @property
  def trained_samples(self):
    return self.regressor.training_samples

  @property
  def model_type(self):
    return self.regressor.__class__.__name__

  def _train_model(self, training_data, log):
    self.regressor.partial_fit(training_data[:, :-1], training_data[:, -1])
    self.regressor.training_samples += len(training_data)
    return self.regressor.loss_

  def _predict_scores(self, states):
    return self.regressor.predict(states)

  @staticmethod
  def _create_or_load_model(regressor_constructor, log, regressor_name=None):
    """
    Creates a new regressor model. Either loads an existing or creates a new regressor.

    :regressor_constructor: Constructor to instantiate a new regressor.
    :log: Logger instance.
    :regressor_name: Optional: Name of the regressor obtain. Uses the config's name if not specified.

    :returns: Regressor instance.
    """
    assert Config.FORCE_GAME_TYPE, "learner players are currently for specific game types only"

    # ensure there's a loss file with the expected header
    if Config.ONLINE_TRAINING and not os.path.exists(Config.LOSS_FILE):
      with open(Config.LOSS_FILE, "w") as fh:
        fh.write("samples,loss\n")

    pickle_file_name = "{}/{}".format(Config.MODEL_DIRECTORY, regressor_name or Config.REGRESSOR_NAME)
    if os.path.exists(pickle_file_name):
      return SklearnPlayer._load_model(regressor_constructor, pickle_file_name, log)
    return SklearnPlayer._create_model(regressor_constructor, log)

  @staticmethod
  def _load_model(regressor_constructor, pickle_file_name, log):
    with open(pickle_file_name, "rb") as fh:
      regressor = pickle.load(fh)

    if not hasattr(regressor, "game_type"):
      # previously, the regressors didn't know/care about their game type
      regressor.game_type = Config.FORCE_GAME_TYPE

    real_path = os.path.realpath(pickle_file_name)[len(os.getcwd())+1:]
    path_difference = "" if real_path == pickle_file_name else " ({})".format(real_path)
    log.info("Loaded regressor from {}{} for {} (trained on {} hands - {} hands, loss {:.1f})".format(
      pickle_file_name, path_difference, regressor.game_type.name,
      utils.format_human(regressor.training_samples/Const.DECISIONS_PER_HAND),
      utils.format_human(regressor.training_samples/32), regressor.loss_))
    log.info("Regressor details: {}".format(regressor))

    assert regressor.__class__.__name__ == regressor_constructor.__name__, \
        "Loaded regressor is a different instance type than desired, aborting"
    assert regressor.game_type == Config.FORCE_GAME_TYPE, "Loaded regressor is for a different game type, aborting"

    if Config.ONLINE_TRAINING:
      # this is a bit of a crutch to avoid writing the loss when creating the LC... TODO: check if that's needed
      with open(Config.LOSS_FILE, "a") as fh:
        fh.write("{},{}\n".format(regressor.training_samples, regressor.loss_))

    return regressor

  @staticmethod
  def _create_model(regressor_constructor, log):
    assert Config.LOAD_TRAINING_DATA_FILE_NAME and os.path.exists(Config.LOAD_TRAINING_DATA_FILE_NAME), \
        "Found neither regressor '{}' nor training data file '{}'".format(
            Config.REGRESSOR_NAME, Config.LOAD_TRAINING_DATA_FILE_NAME)

    regressor_args = Config.TEAM_1_MODEL_ARGS or {}
    if regressor_args:
      log.warning("Applying custom arguments: '{}'".format(regressor_args))
    regressor_args["warm_start"] = True

    # instantiate new regressor and add custom fields
    regressor = regressor_constructor(**regressor_args)
    regressor.training_samples = 0
    regressor.game_type = Config.FORCE_GAME_TYPE

    log.warning("New regressor: {}".format(regressor))

    return regressor

  def checkpoint(self, current_iteration, total_iterations, log):
    unformatted_file_name = "{}_{}_{:0" + str(int(math.log10(total_iterations))+1) + "d}.pkl"
    file_name = unformatted_file_name.format(self.name,
        self.regressor.__class__.__name__, current_iteration)
    file_path = "{}/{}".format(Config.EVALUATION_DIRECTORY, file_name)
    log.info("Storing regressor in '{}' at iteration {}/{} ({:.1f}%)".format(file_name,
      utils.format_human(current_iteration), utils.format_human(total_iterations),
      100.0*current_iteration/total_iterations))

    with open(file_path, "wb") as fh:
      pickle.dump(self.regressor, fh)


class SgdPlayer(SklearnPlayer):
  """
  ML-player using a Stochastic Gradient Descent model.
  """

  _sgd_regressor = None

  def __init__(self, name, number, log):
    offline_training = False
    if SgdPlayer._sgd_regressor is None:
      SgdPlayer._sgd_regressor = SklearnPlayer._create_or_load_model(SGDRegressor, log)
      offline_training = True
    super(SgdPlayer, self).__init__(name, number, SgdPlayer._sgd_regressor, offline_training, log)


class MlpPlayer(SklearnPlayer):
  """
  ML-player using a Multilayer Perceptron model.
  """

  _mlp_regressor = None

  def __init__(self, name, number, log):
    offline_training = False
    if MlpPlayer._mlp_regressor is None:
      MlpPlayer._mlp_regressor = SklearnPlayer._create_or_load_model(MLPRegressor, log)
      offline_training = True
    super(MlpPlayer, self).__init__(name, number, MlpPlayer._mlp_regressor, offline_training, log)


class OtherMlpPlayer(SklearnPlayer):
  """
  Another ML-player using a Multilayer Perceptron model.
  """

  _mlp_regressor = None

  def __init__(self, name, number, log):
    offline_training = False
    if OtherMlpPlayer._mlp_regressor is None:
      log.fatal("WARNING: If the other regressor is trained on an incompatible encoding, it probably won't work!")
      OtherMlpPlayer._mlp_regressor = SklearnPlayer._create_or_load_model(MLPRegressor, log,
          regressor_name=Config.OTHER_REGRESSOR_NAME)
      offline_training = True
    super(OtherMlpPlayer, self).__init__(name, number, OtherMlpPlayer._mlp_regressor, offline_training, log,
        regressor_name=Config.OTHER_REGRESSOR_NAME)
