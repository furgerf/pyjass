#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import Config
from itertools import permutations
from unittest import TestCase
from unittest.mock import MagicMock

import numpy as np

from baseline_players import RandomCardPlayer
from card import Card
from const import Const
from encoding import Encoding
from game_type import GameType
from parameterized import parameterized
from player import Player
from utils import flatten


class PlayerTest(TestCase):
  # pylint: disable=invalid-name,protected-access,line-too-long

  @classmethod
  def setUpClass(cls):
    Config.ENCODING = Encoding("better", [1, 2, 3, 4], 5, [10, 15, 20], 50, 0, 0,
        relative_in_play_encoding=True, trump_code_offset=100)

  def verify_card_permutations(self, all_cards_by_suit, correct_order, cards_by_suit):
    all_permutations = PlayerTest.get_permutations_by_suit(all_cards_by_suit) if cards_by_suit \
        else PlayerTest.get_permutations_by_value(all_cards_by_suit)

    for permutation in all_permutations:
      self.assertTrue(np.array_equal(Player._sort_decision_state(permutation, cards_by_suit), correct_order))

  @staticmethod
  def get_permutations_by_suit(cards_by_suit):
    return [flatten(permutation) for permutation in permutations(cards_by_suit)]

  @staticmethod
  def get_permutations_by_value(cards_by_suit):
    return [flatten(zip(*permutation)) for permutation in permutations(cards_by_suit)]

  @staticmethod
  def get_correct_decision_state(cards, order, cards_by_suit):
    ordered_cards = [cards[i] for i in order]
    if cards_by_suit:
      return flatten(ordered_cards)
    return flatten(zip(*ordered_cards))

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
    for _ in range(int(1e2)):
      all_cards = [
          list(np.random.randint(0, 255, Const.CARDS_PER_SUIT)),
          list(np.random.randint(0, 255, Const.CARDS_PER_SUIT)),
          list(np.random.randint(0, 255, Const.CARDS_PER_SUIT)),
          list(np.random.randint(0, 255, Const.CARDS_PER_SUIT))
          ]
      first_order = Player._sort_decision_state(
          PlayerTest.get_correct_decision_state(all_cards, range(Const.SUIT_COUNT), cards_by_suit), cards_by_suit)
      self.verify_card_permutations(all_cards, first_order, cards_by_suit)

  @parameterized.expand([
    [GameType.OBENABE],
    [GameType.UNNENUFE]
    ])
  def test_get_valid_cards_to_play_non_trump(self, game_type):
    testee = RandomCardPlayer("testee", 0, MagicMock())
    testee.hand = [
        Card(Card.SPADES, 5), # J
        Card(Card.HEARTS, 0), # 6
        Card(Card.HEARTS, 7), # K
        Card(Card.CLUBS, 3), # 9
        ]

    # no cards played yet
    self.assertEqual(testee.get_valid_cards_to_play([], game_type), testee.hand)

    # can't match suit
    self.assertEqual(testee.get_valid_cards_to_play([Card(Card.DIAMONDS, 1)], game_type), testee.hand)
    self.assertEqual(testee.get_valid_cards_to_play([
      Card(Card.DIAMONDS, 1), Card(Card.SPADES, 1), Card(Card.HEARTS, 1)], game_type), testee.hand)

    # can match suit
    self.assertEqual(testee.get_valid_cards_to_play([Card(Card.SPADES, 1)], game_type), [Card(Card.SPADES, 5)])
    self.assertEqual(testee.get_valid_cards_to_play([Card(Card.HEARTS, 1)], game_type),
        [Card(Card.HEARTS, 0), Card(Card.HEARTS, 7)])
    self.assertEqual(testee.get_valid_cards_to_play([Card(Card.CLUBS, 1)], game_type), [Card(Card.CLUBS, 3)])

  def test_get_valid_cards_to_play_trump(self):
    testee = RandomCardPlayer("testee", 0, MagicMock())
    testee.hand = [
        Card(Card.SPADES, 5), # J
        Card(Card.HEARTS, 5), # J
        Card(Card.HEARTS, 7), # K
        Card(Card.CLUBS, 3), # 9
        ]

    # non-trump is played without any trump in play
    game_type = GameType.TRUMP_HEARTS
    played_cards = [Card(Card.SPADES, 1)]
    for card in testee.hand + played_cards:
      card.set_game_type(game_type)
    self.assertEqual(testee.get_valid_cards_to_play(played_cards, game_type), [Card(Card.SPADES, 5), Card(Card.HEARTS, 5), Card(Card.HEARTS, 7)])

    game_type = GameType.TRUMP_CLUBS
    played_cards = [Card(Card.SPADES, 1), Card(Card.DIAMONDS, 3)]
    for card in testee.hand + played_cards:
      card.set_game_type(game_type)
    self.assertEqual(testee.get_valid_cards_to_play(played_cards, game_type), [Card(Card.SPADES, 5), Card(Card.CLUBS, 3)])

    # non-trump is played which can't be matched without any trump in play
    game_type = GameType.TRUMP_HEARTS
    played_cards = [Card(Card.DIAMONDS, 1), Card(Card.CLUBS, 8)]
    for card in testee.hand + played_cards:
      card.set_game_type(game_type)
    self.assertEqual(testee.get_valid_cards_to_play(played_cards, game_type), [Card(Card.SPADES, 5), Card(Card.HEARTS, 5), Card(Card.HEARTS, 7), Card(Card.CLUBS, 3)])

    # non-trump is played with a trump in play
    game_type = GameType.TRUMP_HEARTS
    played_cards = [Card(Card.SPADES, 1), Card(Card.HEARTS, 8)]
    for card in testee.hand + played_cards:
      card.set_game_type(game_type)
    self.assertEqual(testee.get_valid_cards_to_play(played_cards, game_type), [Card(Card.SPADES, 5), Card(Card.HEARTS, 5)]) # not allowed to play K (undertrump)

    # non-trump is played with two trumps in play
    game_type = GameType.TRUMP_HEARTS
    played_cards = [Card(Card.SPADES, 1), Card(Card.HEARTS, 0), Card(Card.HEARTS, 8)]
    for card in testee.hand + played_cards:
      card.set_game_type(game_type)
    self.assertEqual(testee.get_valid_cards_to_play(played_cards, game_type), [Card(Card.SPADES, 5), Card(Card.HEARTS, 5)]) # not allowed to play K (undertrump)

    # non-trump is played which can't be matched with a trump in play
    game_type = GameType.TRUMP_HEARTS
    played_cards = [Card(Card.DIAMONDS, 1), Card(Card.HEARTS, 8)]
    for card in testee.hand + played_cards:
      card.set_game_type(game_type)
    self.assertEqual(testee.get_valid_cards_to_play(played_cards, game_type), [Card(Card.SPADES, 5), Card(Card.HEARTS, 5), Card(Card.CLUBS, 3)]) # STILL not allowed to play K (undertrump)

    # trump is played
    game_type = GameType.TRUMP_HEARTS
    played_cards = [Card(Card.HEARTS, 1), Card(Card.HEARTS, 2)]
    for card in testee.hand + played_cards:
      card.set_game_type(game_type)
    self.assertEqual(testee.get_valid_cards_to_play(played_cards, game_type), [Card(Card.HEARTS, 5), Card(Card.HEARTS, 7)])

    game_type = GameType.TRUMP_SPADES
    played_cards = [Card(Card.SPADES, 1), Card(Card.SPADES, 2)]
    for card in testee.hand + played_cards:
      card.set_game_type(game_type)
    self.assertEqual(testee.get_valid_cards_to_play(played_cards, game_type), testee.hand)

    testee.hand = [
        Card(Card.HEARTS, 5), # J
        Card(Card.HEARTS, 7), # K
        ]

    # untertrumping is allowed if there are only trumps in the hand
    played_cards = [Card(Card.DIAMONDS, 1), Card(Card.HEARTS, 8)]
    for card in testee.hand + played_cards:
      card.set_game_type(game_type)
    self.assertEqual(testee.get_valid_cards_to_play(played_cards, game_type), [Card(Card.HEARTS, 5), Card(Card.HEARTS, 7)])

  def test_convert_to_relative_invalid(self):
    testee = RandomCardPlayer("testee", 0, MagicMock())

    # the player number must be among the valid codes and specifically, among the player codes
    self.assertRaises(AssertionError, lambda: testee.convert_to_relative(6))
    self.assertRaises(AssertionError, lambda: testee.convert_to_relative(106))
    self.assertRaises(AssertionError, lambda: testee.convert_to_relative(10))
    self.assertRaises(AssertionError, lambda: testee.convert_to_relative(50))

    # unknown cards are ok and stay unknown
    self.assertEqual(testee.convert_to_relative(0), 0)

  def test_convert_to_relative_non_trump(self):
    # non-trump in -> non-trump out
    testee = RandomCardPlayer("testee", 1, MagicMock())
    self.assertEqual(testee.convert_to_relative(1), 1)
    self.assertEqual(testee.convert_to_relative(2), 2)
    self.assertEqual(testee.convert_to_relative(3), 3)
    self.assertEqual(testee.convert_to_relative(4), 4)

    testee = RandomCardPlayer("testee", 2, MagicMock())
    self.assertEqual(testee.convert_to_relative(1), 4)
    self.assertEqual(testee.convert_to_relative(2), 1)
    self.assertEqual(testee.convert_to_relative(3), 2)
    self.assertEqual(testee.convert_to_relative(4), 3)

    testee = RandomCardPlayer("testee", 3, MagicMock())
    self.assertEqual(testee.convert_to_relative(1), 3)
    self.assertEqual(testee.convert_to_relative(2), 4)
    self.assertEqual(testee.convert_to_relative(3), 1)
    self.assertEqual(testee.convert_to_relative(4), 2)

    testee = RandomCardPlayer("testee", 4, MagicMock())
    self.assertEqual(testee.convert_to_relative(1), 2)
    self.assertEqual(testee.convert_to_relative(2), 3)
    self.assertEqual(testee.convert_to_relative(3), 4)
    self.assertEqual(testee.convert_to_relative(4), 1)

  def test_convert_to_relative_trump(self):
    # trump in -> trump out
    testee = RandomCardPlayer("testee", 1, MagicMock())
    self.assertEqual(testee.convert_to_relative(101), 101)
    self.assertEqual(testee.convert_to_relative(102), 102)
    self.assertEqual(testee.convert_to_relative(103), 103)
    self.assertEqual(testee.convert_to_relative(104), 104)

    testee = RandomCardPlayer("testee", 2, MagicMock())
    self.assertEqual(testee.convert_to_relative(101), 104)
    self.assertEqual(testee.convert_to_relative(102), 101)
    self.assertEqual(testee.convert_to_relative(103), 102)
    self.assertEqual(testee.convert_to_relative(104), 103)

    testee = RandomCardPlayer("testee", 3, MagicMock())
    self.assertEqual(testee.convert_to_relative(101), 103)
    self.assertEqual(testee.convert_to_relative(102), 104)
    self.assertEqual(testee.convert_to_relative(103), 101)
    self.assertEqual(testee.convert_to_relative(104), 102)

    testee = RandomCardPlayer("testee", 4, MagicMock())
    self.assertEqual(testee.convert_to_relative(101), 102)
    self.assertEqual(testee.convert_to_relative(102), 103)
    self.assertEqual(testee.convert_to_relative(103), 104)
    self.assertEqual(testee.convert_to_relative(104), 101)
