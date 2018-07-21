#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Score:
  def __init__(self):
    self.total_score_team_1 = 0
    self.total_score_team_2 = 0
    self.wins_team_1 = 0
    self.wins_team_2 = 0

  @property
  def score_data(self):
    # returns the score data in the expected format for the checkpoints
    return self.wins_team_1, self.total_score_team_1, self.wins_team_2, self.total_score_team_2

  @property
  def team_1_win_percentage(self):
    if self.wins_team_1 + self.wins_team_2 == 0:
      return 0
    return 100.0 * self.wins_team_1 / (self.wins_team_1 + self.wins_team_2)

  def add_scores(self, team_1_score, team_2_score):
    self.total_score_team_1 += team_1_score
    self.total_score_team_2 += team_2_score

  def add_other_score(self, other_score):
    self.total_score_team_1 += other_score.total_score_team_1
    self.total_score_team_2 += other_score.total_score_team_2
    self.wins_team_1 += other_score.wins_team_1
    self.wins_team_2 += other_score.wins_team_2

  def add_win(self, team_1):
    if team_1:
      self.wins_team_1 += 1
    else:
      self.wins_team_2 += 1

  def clear(self):
    self.total_score_team_1 = 0
    self.total_score_team_2 = 0
    self.wins_team_1 = 0
    self.wins_team_2 = 0
