#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

from player import Player


class RandomCardPlayer(Player):
  def _select_card(self, args):
    valid_cards = args[0]
    return valid_cards[np.random.randint(len(valid_cards))]


class HighestCardPlayer(Player):
  def _select_card(self, args):
    valid_cards = args[0]
    return valid_cards[-1]
