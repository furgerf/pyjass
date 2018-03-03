#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pylint: disable=unused-import
import csv
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
import numpy as np
import pandas as pd
# import seaborn as sns
import pickle

from src import utils

plt.ion()


def load_model(file_name):
  with open(file_name, "rb") as fh:
    return pickle.load(fh)

def store_model(model, file_name):
  with open(file_name, "wb") as fh:
    return pickle.dump(model, fh)


def visualize_scores(eid="foo", ymin=0.0, ymax=1.0):
  scores_file = "evaluations/{}/scores.csv".format(eid)
  df = pd.read_csv(scores_file)

  # prepare data
  df["win_percentage"] = df.wins_team_1 / (df.wins_team_1 + df.wins_team_2)
  df["score_percentage"] = df.score_team_1 / (df.score_team_1 + df.score_team_2)

  df["cum_wins_team_1"] = df.wins_team_1.cumsum()
  df["cum_wins_team_2"] = df.wins_team_2.cumsum()
  df["cum_score_team_1"] = df.score_team_1.cumsum()
  df["cum_score_team_2"] = df.score_team_2.cumsum()
  df["cum_win_percentage"] = df.cum_wins_team_1 / (df.cum_wins_team_1 + df.cum_wins_team_2)
  df["cum_score_percentage"] = df.cum_score_team_1 / (df.cum_score_team_1 + df.cum_score_team_2)

  # plot
  fig = plt.figure()
  ax = fig.add_subplot(111)
  ax.xaxis.set_major_formatter(EngFormatter())
  ax.yaxis.set_major_locator(plt.MultipleLocator(0.05))
  ax.minorticks_on()
  plt.title("{}: Team 1 win/score percentage".format(eid))
  plt.ylim(ymin, ymax)
  plt.grid()
  plt.tight_layout()

  plt.plot(df.hand, df.win_percentage, "k.-", c="g", alpha=0.3, label="Team 1 win %")
  plt.plot(df.hand, df.score_percentage, "k.-", c="b", alpha=0.3, label="Team 1 score %")
  plt.plot(df.hand, df.cum_win_percentage, "k.-", c="g", label="Cum team 1 win %")
  plt.plot(df.hand, df.cum_score_percentage, "k.-", c="b", label="Cum team 1 score %")

  plt.axhline(y=0.5, c="r", alpha=0.3, linestyle="--")

  if "team_1_info" in df.columns and "team_2_info" in df.columns:
    for i, index in enumerate(df.team_1_info.diff()[df.team_1_info.diff() != 0].index.values):
      # NOTE: both teams have the same training interval
      row = df.iloc[index]

      if pd.isnull(row.team_1_info) and pd.isnull(row.team_2_info):
        continue

      plt.axvline(x=row.hand, c="purple", alpha=0.5, linestyle="-")
      if not pd.isnull(row.team_1_info) and not pd.isnull(row.team_2_info):
        note = "T1:{}\nT2:{}".format(utils.format_human(row.team_1_info), utils.format_human(row.team_2_info))
      elif not pd.isnull(row.team_1_info):
        note = "T1:{}".format(utils.format_human(row.team_1_info))
      elif not pd.isnull(row.team_2_info):
        note = "T2:{}".format(utils.format_human(row.team_2_info))

      plt.annotate(note, color="purple",
          xy=(row.hand, plt.ylim()[0] + 0.01 + 0.02*(i%4)), xytext=(row.hand, plt.ylim()[0] + 0.01 + 0.02*(i%4)))

  plt.legend()
  plt.show()

  return df
