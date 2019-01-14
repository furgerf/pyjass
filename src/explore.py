#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pylint: disable=unused-import,too-many-statements
import csv
import os
import pickle
import re

import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
import numpy as np
import pandas as pd
from keras.layers import Activation, Dense
from keras.models import Sequential

import utils

plt.ion()


def load_model(file_name):
  with open(file_name, "rb") as fh:
    return pickle.load(fh)

def store_model(model, file_name):
  with open(file_name, "wb") as fh:
    return pickle.dump(model, fh)


def visualize_scores(eid, loss_max=1000):
  scores_file = "evaluations/{}/scores.csv".format(eid)
  curve_scores_file = "evaluations/{}/curve_scores.csv".format(eid)
  loss_file = "evaluations/{}/loss.csv".format(eid)

  scores = pd.read_csv(scores_file) if os.path.exists(scores_file) else None
  loss = pd.read_csv(loss_file) if os.path.exists(loss_file) else None

  if scores is None:
    print("Scores file '{}' not found".format(curve_scores_file))
    scores = pd.read_csv(curve_scores_file) if os.path.exists(curve_scores_file) else None
    if scores is None:
      print("Curve scores file '{}' *ALSO* not found".format(curve_scores_file))
  if loss is None:
    print("loss file '{}' not found".format(loss_file))

  # plot
  fig = plt.figure()
  plt.grid()

  # score_ax = fig.add_subplot(111)
  score_ax = fig.axes[0]
  score_ax.xaxis.set_major_formatter(EngFormatter())
  score_ax.yaxis.set_major_locator(plt.MultipleLocator(0.05))
  score_ax.minorticks_on()
  score_ax.set_ylim(0, 1)

  if scores is not None:
    scores["win_percentage"] = scores.wins_team_1 / (scores.wins_team_1 + scores.wins_team_2)
    win_percentage_mean = scores.groupby("team_1_info").mean()
    win_percentage_std = scores.groupby("team_1_info").std()
    win_percentage_rolling = win_percentage_mean.win_percentage.rolling(3, center=True).mean()
    scores["score_percentage"] = scores.score_team_1 / (scores.score_team_1 + scores.score_team_2)
    score_percentage_mean = scores.groupby("team_1_info").mean()
    score_percentage_std = scores.groupby("team_1_info").std()
    score_percentage_rolling = score_percentage_mean.score_percentage.rolling(3, center=True).mean()

    score_ax.fill_between(win_percentage_mean.index / 32,
        win_percentage_mean.win_percentage - win_percentage_std.win_percentage,
        win_percentage_mean.win_percentage + win_percentage_std.win_percentage,
        alpha=0.1, color="g")
    score_ax.plot(win_percentage_mean.index / 32, win_percentage_mean.win_percentage,
        ".-", c="g", markersize=10, linewidth=1, label="Team 1 win %")
    score_ax.plot(win_percentage_mean.index / 32, win_percentage_rolling,
        "-", c="g", alpha=0.5, linewidth=3, label="Rolling win %")

    score_ax.fill_between(score_percentage_mean.index / 32,
        score_percentage_mean.score_percentage - score_percentage_std.score_percentage,
        score_percentage_mean.score_percentage + score_percentage_std.score_percentage,
        alpha=0.1, color="b")
    score_ax.plot(score_percentage_mean.index / 32, score_percentage_mean.score_percentage,
        ".-", c="b", markersize=10, linewidth=1, label="Team 1 score %")
    score_ax.plot(score_percentage_mean.index / 32, score_percentage_rolling,
        "-", c="b", alpha=0.5, linewidth=3, label="Rolling score %")

  if loss is not None:
    loss_ax = score_ax.twinx()
    loss_ax.set_ylim(0, loss_max)

    loss["loss_rolling"] = loss.loss.rolling(3, center=True).mean()

    loss_ax.plot(loss.samples / 32, loss.loss,
        ".-", c="r", markersize=10, linewidth=1, label="Loss")
    loss_ax.plot(loss.samples / 32, loss.loss_rolling,
        "-", c="r", alpha=0.5, linewidth=3, label="Rolling loss")


  score_ax.axhline(y=0.5, c="r", alpha=0.3, linestyle="--")

  # plot training lines
  if scores is not None and "team_1_info" in scores.columns and "team_2_info" in scores.columns:
    for i, index in enumerate(scores.team_1_info.diff()[scores.team_1_info.diff() != 0].index.values):
      # NOTE: both teams have the same training interval
      row = scores.iloc[index]

      if pd.isnull(row.team_1_info) and pd.isnull(row.team_2_info):
        continue

      plt.axvline(x=row.team_1_info / 32, c="purple", alpha=0.5, linestyle="-")
      if not pd.isnull(row.team_1_info) and not pd.isnull(row.team_2_info):
        note = "T1:{}\nT2:{}".format(utils.format_human(row.team_1_info), utils.format_human(row.team_2_info))
      elif not pd.isnull(row.team_1_info):
        note = "T1:{}".format(utils.format_human(row.team_1_info))
      elif not pd.isnull(row.team_2_info):
        note = "T2:{}".format(utils.format_human(row.team_2_info))

      score_ax.annotate(note, color="purple",
          xy=(row.team_1_info / 32, plt.ylim()[0] + 0.01 + 0.02*(i%4)),
          xytext=(row.team_1_info / 32, plt.ylim()[0] + 0.01 + 0.02*(i%4)))

  if loss is not None:
    loss_ax.legend(loc="upper right")
  if scores is not None:
    score_ax.legend(loc="lower left")

  plt.title("{}: Team 1 win/score percentage".format(eid))
  plt.tight_layout()
  plt.show()

  return scores, loss


def compare_loss_performance(model_number, verbose=False):
  with open("models/{}/description.md".format(model_number)) as fh:
    lines = fh.readlines()

  data = {}

  current_round = None
  for line in lines:
    line = line.strip()
    round_match = re.match(r"# round (\d+).*", line, re.IGNORECASE)
    if round_match:
      current_round = int(round_match.group(1))
      if verbose:
        print("Parsing round {}".format(current_round))
      continue

    model_match = re.match(r"^([-_A-z0-9]+): ([.\d]+)/([.\d]+)%, loss: ([.\d]+).*", line)
    if model_match:
      model = model_match.group(1)
      trained_percentage = float(model_match.group(2))
      training_percentage = float(model_match.group(3))
      loss = float(model_match.group(4))
      if model not in data:
        data[model] = []
      assert len(data[model]) == current_round-1, "Round mismatch for {}, current round: {}, data entries: {}".format(
          model, current_round, len(data[model]))
      data[model].append((trained_percentage, training_percentage, loss))
      if verbose:
        print("{} had {} and {}% with loss {} ('{}')".format(
          model, trained_percentage, training_percentage, loss, line))
      continue

    hands_match = re.match(r"^=> \d+M hands$", line)
    if hands_match:
      # ignore the number of played hands
      continue

    if not current_round or not line:
      # ignore header and empty lines
      continue

    print("*** Unmatched line: '{}'".format(line))

  fig = plt.figure()
  plt.title("Model {}".format(model_number))
  plt.grid()
  plt.xlabel("Round")
  plt.xticks(range(current_round), range(1, current_round + 1))

  score_ax = fig.axes[0]
  score_ax.set_ylabel("Training score")
  score_ax.axhline(y=50, c="r", linestyle="--")
  loss_ax = score_ax.twinx()
  loss_ax.set_ylabel("Loss")

  for model, metrics in data.items():
    scores = [m[0] for m in metrics]
    losses = [m[-1] for m in metrics]
    score_ax.plot(scores, label="{}: scores".format(model))
    loss_ax.plot(losses, label="{}: losses".format(model), alpha=0.5, ls="--")

  fig.legend()
