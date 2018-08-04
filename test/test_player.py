#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import permutations
from unittest import TestCase

import numpy as np

from const import Const
from parameterized import parameterized
from player import Player


class PlayerTest(TestCase):
  # pylint: disable=invalid-name,protected-access

  def verify_card_permutations(self, all_cards_by_suit, correct_order, cards_by_suit):
    all_permutations = PlayerTest.get_permutations_by_suit(all_cards_by_suit) if cards_by_suit \
        else PlayerTest.get_permutations_by_value(all_cards_by_suit)

    for permutation in all_permutations:
      foo = Player._sort_decision_state(permutation, cards_by_suit)
      self.assertTrue(np.array_equal(Player._sort_decision_state(permutation, cards_by_suit), correct_order))

  @staticmethod
  def get_permutations_by_suit(cards_by_suit):
    return [[item for sublist in permutation for item in sublist] for permutation in permutations(cards_by_suit)]

  @staticmethod
  def get_permutations_by_value(cards_by_suit):
    return [[item for sublist in zip(*permutation) for item in sublist] for permutation in permutations(cards_by_suit)]

  @staticmethod
  def get_correct_decision_state(cards, order, cards_by_suit):
    ordered_cards = [cards[i] for i in order]
    if cards_by_suit:
      return [item for sublist in ordered_cards for item in sublist]
    return [item for sublist in zip(*ordered_cards) for item in sublist]

  @parameterized.expand([
    [True],
    [False]
    ])
  def test_sort_decision_state(self, cards_by_suit):
    all_cards = [
        [1] * Const.CARDS_PER_SUIT,
        [2] * Const.CARDS_PER_SUIT,
        [3] * Const.CARDS_PER_SUIT,
        [4] * Const.CARDS_PER_SUIT
        ]
    correct_state = PlayerTest.get_correct_decision_state(all_cards, range(Const.SUIT_COUNT), cards_by_suit)
    self.verify_card_permutations(all_cards, correct_state, cards_by_suit)
    all_cards = [
        [0] * Const.CARDS_PER_SUIT,
        [100] * Const.CARDS_PER_SUIT,
        [10] * Const.CARDS_PER_SUIT,
        [255] * Const.CARDS_PER_SUIT
        ]
    correct_state = PlayerTest.get_correct_decision_state(all_cards, [0, 2, 1, 3], cards_by_suit)
    self.verify_card_permutations(all_cards, correct_state, cards_by_suit)

    all_cards = [
        [0] * Const.CARDS_PER_SUIT,
        [0] * Const.CARDS_PER_SUIT,
        [0] * Const.CARDS_PER_SUIT,
        [0] * Const.CARDS_PER_SUIT
        ]
    all_cards[0][3] = 1
    all_cards[1][2] = 1
    all_cards[2][1] = 1
    all_cards[3][0] = 1
    correct_state = PlayerTest.get_correct_decision_state(all_cards, range(Const.SUIT_COUNT), cards_by_suit)
    self.verify_card_permutations(all_cards, correct_state, cards_by_suit)
    all_cards = [
        [0] * Const.CARDS_PER_SUIT,
        [0] * Const.CARDS_PER_SUIT,
        [0] * Const.CARDS_PER_SUIT,
        [0] * Const.CARDS_PER_SUIT
        ]
    all_cards[0][0] = 1
    all_cards[1][0] = 2
    all_cards[2][0] = 3
    all_cards[3][0] = 4
    correct_state = PlayerTest.get_correct_decision_state(all_cards, range(Const.SUIT_COUNT), cards_by_suit)
    self.verify_card_permutations(all_cards, correct_state, cards_by_suit)
    all_cards = [
        [0] * Const.CARDS_PER_SUIT,
        [0] * Const.CARDS_PER_SUIT,
        [0] * Const.CARDS_PER_SUIT,
        [0] * Const.CARDS_PER_SUIT
        ]
    all_cards[3][-1] = 1
    all_cards[1][-1] = 2
    all_cards[0][-1] = 3
    all_cards[2][-1] = 4
    correct_state = PlayerTest.get_correct_decision_state(all_cards, [3, 1, 0, 2], cards_by_suit)
    self.verify_card_permutations(all_cards, correct_state, cards_by_suit)

    all_cards = [range(i*Const.CARDS_PER_SUIT, (i+1)*Const.CARDS_PER_SUIT) for i in range(Const.SUIT_COUNT)]
    correct_state = PlayerTest.get_correct_decision_state(all_cards, range(Const.SUIT_COUNT), cards_by_suit)
    self.verify_card_permutations(all_cards, correct_state, cards_by_suit)
    all_cards = [range(i*Const.CARDS_PER_SUIT, (i+1)*Const.CARDS_PER_SUIT) for i in range(Const.SUIT_COUNT-1, -1, -1)]
    correct_state = PlayerTest.get_correct_decision_state(all_cards, range(Const.SUIT_COUNT-1, -1, -1), cards_by_suit)
    self.verify_card_permutations(all_cards, correct_state, cards_by_suit)

  @parameterized.expand([
    [True],
    [False]
    ])
  def test_sort_decision_state_randomized(self, cards_by_suit):
    np.random.seed(42)
    for _ in range(int(1e3)):
      all_cards = [
          list(np.random.randint(0, 255, Const.CARDS_PER_SUIT)),
          list(np.random.randint(0, 255, Const.CARDS_PER_SUIT)),
          list(np.random.randint(0, 255, Const.CARDS_PER_SUIT)),
          list(np.random.randint(0, 255, Const.CARDS_PER_SUIT))
          ]
      first_order = Player._sort_decision_state(
          PlayerTest.get_correct_decision_state(all_cards, range(Const.SUIT_COUNT), cards_by_suit), cards_by_suit)
      self.verify_card_permutations(all_cards, first_order, cards_by_suit)
