#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import abstractmethod

import numpy as np

from player import Player


class BaselinePlayer(Player):
  def train(self, training_data):
    pass

  def checkpoint(self, current_iteration, total_iterations):
    pass

  @abstractmethod
  def _select_card(self, args):
    pass

  def get_checkpoint_data(self):
    return None


class RandomCardPlayer(BaselinePlayer):
  def _select_card(self, args):
    valid_cards = args[0]
    return valid_cards[np.random.randint(len(valid_cards))]


class HighestCardPlayer(BaselinePlayer):
  def _select_card(self, args):
    valid_cards = args[0]
    return valid_cards[-1]
