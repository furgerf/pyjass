#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import permutations
from unittest import TestCase

import numpy as np

from const import Const
from player import Player


class PlayerTest(TestCase):
  # pylint: disable=invalid-name,protected-access

  def verify_card_permutations(self, all_cards, order):
    for equivalent_order in permutations(all_cards):
      self.assertTrue(np.array_equal(Player._sort_decision_state(
        [item for sublist in equivalent_order for item in sublist]), order))

  def test_sort_decision_state(self):
    a = [1] * Const.CARDS_PER_PLAYER
    b = [2] * Const.CARDS_PER_PLAYER
    c = [3] * Const.CARDS_PER_PLAYER
    d = [4] * Const.CARDS_PER_PLAYER
    self.verify_card_permutations([a, b, c, d], a + b + c + d)
    a = [0] * Const.CARDS_PER_PLAYER
    b = [10] * Const.CARDS_PER_PLAYER
    c = [100] * Const.CARDS_PER_PLAYER
    d = [255] * Const.CARDS_PER_PLAYER
    self.verify_card_permutations([a, b, c, d], a + b + c + d)

    a = [0] * Const.CARDS_PER_PLAYER
    b = [0] * Const.CARDS_PER_PLAYER
    c = [0] * Const.CARDS_PER_PLAYER
    d = [0] * Const.CARDS_PER_PLAYER
    a[3] = 1
    b[2] = 1
    c[1] = 1
    d[0] = 1
    self.verify_card_permutations([a, b, c, d], a + b + c + d)
    a = [0] * Const.CARDS_PER_PLAYER
    b = [0] * Const.CARDS_PER_PLAYER
    c = [0] * Const.CARDS_PER_PLAYER
    d = [0] * Const.CARDS_PER_PLAYER
    a[0] = 1
    b[0] = 2
    c[0] = 3
    d[0] = 4
    self.verify_card_permutations([a, b, c, d], a + b + c + d)
    a = [0] * Const.CARDS_PER_PLAYER
    b = [0] * Const.CARDS_PER_PLAYER
    c = [0] * Const.CARDS_PER_PLAYER
    d = [0] * Const.CARDS_PER_PLAYER
    a[-1] = 1
    b[-1] = 2
    c[-1] = 3
    d[-1] = 4
    self.verify_card_permutations([a, b, c, d], a + b + c + d)

  def test_sort_decision_state_randomized(self):
    np.random.seed(42)
    for _ in range(int(1e3)):
      a = list(np.random.randint(0, 255, Const.CARDS_PER_PLAYER))
      b = list(np.random.randint(0, 255, Const.CARDS_PER_PLAYER))
      c = list(np.random.randint(0, 255, Const.CARDS_PER_PLAYER))
      d = list(np.random.randint(0, 255, Const.CARDS_PER_PLAYER))
      first_order = Player._sort_decision_state(a + b + c + d)
      self.verify_card_permutations([a, b, c, d], first_order)
