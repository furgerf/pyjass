#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import math
import os
import time
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np
from keras.models import load_model, model_from_json

import utils
from config import Config
from const import Const
from game_type import GameType
from learner_player import LearnerPlayer


class KerasPlayer(LearnerPlayer):
  """
  ML-player based on Keras, loading the model architecture from a file.
  """

  _keras_regressor = None

  NAME_FIELD = "name"
  TRAINING_SAMPLES_FIELD = "training_samples"
  GAME_TYPE_FIELD = "game_type"
  LAST_LOSS_FIELD = "last_loss"

  def __init__(self, name, number, log):
    """
    Creates a new keras-based player.

    :name: Name of the player, for display purposes only.
    :number: Number of the player, to determine neighboring players.
    :log: Logger instance.
    """
    offline_training = False
    if KerasPlayer._keras_regressor is None:
      KerasPlayer._keras_regressor, self._training_samples, self._game_type, self._last_loss = \
          KerasPlayer._create_or_load_model(log)
      offline_training = Config.LOAD_TRAINING_DATA_FILE_NAME is not None
    self.regressor = KerasPlayer._keras_regressor
    self.last_training_done = time.time()

    if offline_training:
      # need to define the file name before training (to determine if it's a new model)
      new_model_file_name = "{}/{}".format(Config.MODEL_DIRECTORY, Config.REGRESSOR_NAME)
      existing_model_file_name = "{}/{}-trained-offline.zip".format(Config.EVALUATION_DIRECTORY,
          os.path.splitext(Config.REGRESSOR_NAME)[0])
      trained_model_file = existing_model_file_name if self.training_samples else new_model_file_name
      self._train_regressor_from_file(log)
      log.info("Writing newly-trained regressor to {}".format(trained_model_file))
      self._save_model(trained_model_file)

    super(KerasPlayer, self).__init__(name, number, [Config.FORCE_GAME_TYPE], log)

  @property
  def training_samples(self):
    return self._training_samples

  @property
  def model_type(self):
    return self.regressor.__class__.__name__

  def _train_model(self, training_data, log):
    history = self.regressor.fit(training_data[:, :-1], training_data[:, -1], verbose=0)
    self._training_samples += len(training_data)
    loss = np.mean(history.history["loss"])
    self._last_loss = loss
    return loss

  def _predict_scores(self, states):
    return self.regressor.predict(np.array(states))

  @staticmethod
  def _create_or_load_model(log):
    """
    Creates a new regressor model. Either loads an existing or creates a new regressor.

    :log: Logger instance.

    :returns: Regressor instance.
    """
    assert Config.FORCE_GAME_TYPE, "learner players are currently for specific game types only"

    # ensure there's a loss file with the expected header
    if Config.ONLINE_TRAINING and not os.path.exists(Config.LOSS_FILE):
      with open(Config.LOSS_FILE, "w") as fh:
        fh.write("samples,loss\n")

    model_file_name = "{}/{}".format(Config.MODEL_DIRECTORY, Config.REGRESSOR_NAME)
    if os.path.exists(model_file_name):
      return KerasPlayer._load_model(model_file_name, log)
    return KerasPlayer._create_model(log)

  @staticmethod
  def _load_model(model_path, log):
    with TemporaryDirectory() as temp_dir:
      with ZipFile(model_path, "r") as zip_file:
        zip_file.extractall(temp_dir)

      metadata_path = "{}/info.json".format(temp_dir)
      with open(metadata_path, "r") as fh:
        metadata = json.loads(fh.read())

      training_samples = metadata[KerasPlayer.TRAINING_SAMPLES_FIELD]
      game_type = GameType(metadata[KerasPlayer.GAME_TYPE_FIELD])
      last_loss = metadata[KerasPlayer.LAST_LOSS_FIELD]

      model_path = "{}/{}.h5".format(temp_dir, metadata[KerasPlayer.NAME_FIELD])
      regressor = load_model(model_path)

    real_path = os.path.realpath(model_path)[len(os.getcwd())+1:] # TODO: fix for when model is outside cwd
    path_difference = "" if real_path == model_path else " ({})".format(real_path)
    log.info("Loaded regressor {} from {}{} for {} (trained on {} hands, loss {:.1f})".format(
      metadata[KerasPlayer.NAME_FIELD], model_path, path_difference, game_type,
      utils.format_human(training_samples/Const.DECISIONS_PER_HAND), last_loss))
    log.info("Regressor details")
    regressor.summary()

    assert game_type == Config.FORCE_GAME_TYPE, "Loaded regressor is for a different game type, aborting"

    if Config.ONLINE_TRAINING:
      # this is a bit of a crutch to avoid writing the loss when creating the LC... TODO: check if that's needed
      with open(Config.LOSS_FILE, "a") as fh:
        fh.write("{},{}\n".format(training_samples, last_loss))

    return regressor, training_samples, game_type, last_loss

  @staticmethod
  def _create_model(log):
    assert Config.LOAD_TRAINING_DATA_FILE_NAME and os.path.exists(Config.LOAD_TRAINING_DATA_FILE_NAME), \
        "Found neither regressor '{}' nor training data file '{}'".format(
            Config.REGRESSOR_NAME, Config.LOAD_TRAINING_DATA_FILE_NAME)

    assert Config.TEAM_1_MODEL_ARGS and "file" in dict(Config.TEAM_1_MODEL_ARGS)
    with open("{}/{}".format(Config.ARCHITECTURE_DIRECTORY, dict(Config.TEAM_1_MODEL_ARGS)["file"]), "r") as fh:
      model_json = fh.read()

    # instantiate new regressor and add custom fields
    regressor = model_from_json(model_json)
    training_samples = 0
    game_type = Config.FORCE_GAME_TYPE
    last_loss = None

    log.warning("Using model: '{}'".format(model_json))
    regressor.compile(optimizer="adam", loss="mse", metrics=["mse"])
    regressor.summary()

    return regressor, training_samples, game_type, last_loss

  def _save_model(self, path):
    with TemporaryDirectory() as temp_dir:
      # save model
      model_file_name = os.path.splitext(os.path.basename(path))[0]
      model_path = "{}/{}.h5".format(temp_dir, model_file_name)
      self.regressor.save(model_path)

      # save metadata
      metadata = json.dumps({
        KerasPlayer.NAME_FIELD: model_file_name,
        KerasPlayer.TRAINING_SAMPLES_FIELD: self._training_samples,
        KerasPlayer.GAME_TYPE_FIELD: self._game_type.value,
        KerasPlayer.LAST_LOSS_FIELD: self._last_loss
        })
      metadata_path = "{}/info.json".format(temp_dir)
      with open(metadata_path, "w") as fh:
        fh.write(metadata)

      # zip model and metadata into model file
      with ZipFile(path, "w", ZIP_DEFLATED) as zip_file:
        zip_file.write(model_path, os.path.basename(model_path))
        zip_file.write(metadata_path, os.path.basename(metadata_path))

  def checkpoint(self, current_iteration, total_iterations, log):
    unformatted_file_name = "{}_{}_{:0" + str(int(math.log10(total_iterations))+1) + "d}.zip"
    file_name = unformatted_file_name.format(self.name,
        self.regressor.__class__.__name__, current_iteration)
    file_path = "{}/{}".format(Config.EVALUATION_DIRECTORY, file_name)
    if current_iteration != total_iterations:
      log.info("Storing regressor in '{}' at iteration {}/{} ({:.1f}%)".format(file_name,
        utils.format_human(current_iteration), utils.format_human(total_iterations),
        100.0*current_iteration/total_iterations))
    else:
      log.fatal("Storing final regressor in '{}' with loss {:.1f}".format(file_name, self._last_loss))
    self._save_model(file_path)
