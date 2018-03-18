#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pylint: disable=unused-import
import os
import csv
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
import numpy as np
import pandas as pd
import pickle

import utils

plt.ion()


def load_model(file_name):
  with open(file_name, "rb") as fh:
    return pickle.load(fh)

def store_model(model, file_name):
  with open(file_name, "wb") as fh:
    return pickle.dump(model, fh)


def visualize_scores(eid):
  scores_file = "evaluations/{}/curve_scores.csv".format(eid)
  loss_file = "evaluations/{}/loss.csv".format(eid)

  scores = pd.read_csv(scores_file) if os.path.exists(scores_file) else None
  loss = pd.read_csv(loss_file) if os.path.exists(loss_file) else None

  # plot
  fig = plt.figure()
  plt.grid()

  score_ax = fig.add_subplot(111)
  score_ax.xaxis.set_major_formatter(EngFormatter())
  score_ax.yaxis.set_major_locator(plt.MultipleLocator(0.05))
  score_ax.minorticks_on()
  score_ax.set_ylim(0, 1)

  if scores is not None:
    scores["win_percentage"] = scores.wins_team_1 / (scores.wins_team_1 + scores.wins_team_2)
    scores["score_percentage"] = scores.score_team_1 / (scores.score_team_1 + scores.score_team_2)
    score_ax.plot(scores.team_1_info, scores.win_percentage, "k.-", c="g", label="Team 1 win %")
    score_ax.plot(scores.team_1_info, scores.score_percentage, "k.-", c="b", label="Team 1 score %")

  if loss is not None:
    loss_ax = score_ax.twinx()
    loss_ax.set_ylim(0, 1000)

    loss_ax.plot(loss.samples, loss.loss, "k.-", c="r", label="Model loss")

  score_ax.axhline(y=0.5, c="r", alpha=0.3, linestyle="--")

  if scores is not None and "team_1_info" in scores.columns and "team_2_info" in scores.columns:
    for i, index in enumerate(scores.team_1_info.diff()[scores.team_1_info.diff() != 0].index.values):
      # NOTE: both teams have the same training interval
      row = scores.iloc[index]

      if pd.isnull(row.team_1_info) and pd.isnull(row.team_2_info):
        continue

      plt.axvline(x=row.team_1_info, c="purple", alpha=0.5, linestyle="-")
      if not pd.isnull(row.team_1_info) and not pd.isnull(row.team_2_info):
        note = "T1:{}\nT2:{}".format(utils.format_human(row.team_1_info), utils.format_human(row.team_2_info))
      elif not pd.isnull(row.team_1_info):
        note = "T1:{}".format(utils.format_human(row.team_1_info))
      elif not pd.isnull(row.team_2_info):
        note = "T2:{}".format(utils.format_human(row.team_2_info))

      score_ax.annotate(note, color="purple",
          xy=(row.team_1_info, plt.ylim()[0] + 0.01 + 0.02*(i%4)), xytext=(row.team_1_info, plt.ylim()[0] + 0.01 + 0.02*(i%4)))

  if loss is not None:
    loss_ax.legend()
  score_ax.legend()

  plt.title("{}: Team 1 win/score percentage".format(eid))
  plt.tight_layout()
  plt.show()

  return scores, loss
