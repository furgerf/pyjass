#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase

from card import Card
from parameterized import parameterized
from game_type import GameType


class CardTest(TestCase):
  def setUp(self):
    self.cards_suit_1 = [Card(0, 1), Card(0, 2)]
    self.cards_suit_2 = [Card(1, 1), Card(1, 2)]

  @parameterized.expand([
    [GameType.OBENABE],
    [GameType.TRUMP_HEARTS],
    [GameType.TRUMP_CLUBS],
    [GameType.TRUMP_DIAMONDS],
    [GameType.TRUMP_SPADES],
    ])
  def test_has_worse_value_than_obenabe_trump(self, game_type):
    for card in self.cards_suit_1 + self.cards_suit_2:
      card.set_game_type(game_type)

    self.assertFalse(self.cards_suit_1[0].has_worse_value_than(self.cards_suit_1[0]))
    self.assertTrue(self.cards_suit_1[0].has_worse_value_than(self.cards_suit_1[1]))
    self.assertFalse(self.cards_suit_1[0].has_worse_value_than(self.cards_suit_2[0]))
    self.assertTrue(self.cards_suit_1[0].has_worse_value_than(self.cards_suit_2[1]))

    self.assertFalse(self.cards_suit_1[1].has_worse_value_than(self.cards_suit_1[0]))
    self.assertFalse(self.cards_suit_1[1].has_worse_value_than(self.cards_suit_1[1]))
    self.assertFalse(self.cards_suit_1[1].has_worse_value_than(self.cards_suit_2[0]))
    self.assertFalse(self.cards_suit_1[1].has_worse_value_than(self.cards_suit_2[1]))

  def test_has_worse_value_than_unnenufe(self):
    for card in self.cards_suit_1 + self.cards_suit_2:
      card.set_game_type(GameType.UNNENUFE)

    self.assertFalse(self.cards_suit_1[0].has_worse_value_than(self.cards_suit_1[0]))
    self.assertFalse(self.cards_suit_1[0].has_worse_value_than(self.cards_suit_1[1]))
    self.assertFalse(self.cards_suit_1[0].has_worse_value_than(self.cards_suit_2[0]))
    self.assertFalse(self.cards_suit_1[0].has_worse_value_than(self.cards_suit_2[1]))

    self.assertTrue(self.cards_suit_1[1].has_worse_value_than(self.cards_suit_1[0]))
    self.assertFalse(self.cards_suit_1[1].has_worse_value_than(self.cards_suit_1[1]))
    self.assertTrue(self.cards_suit_1[1].has_worse_value_than(self.cards_suit_2[0]))
    self.assertFalse(self.cards_suit_1[1].has_worse_value_than(self.cards_suit_2[1]))

  def test_is_beaten_by_obenabe(self):
    for card in self.cards_suit_1 + self.cards_suit_2:
      card.set_game_type(GameType.OBENABE)

    self.assertFalse(self.cards_suit_1[0].is_beaten_by(self.cards_suit_1[0]))
    self.assertTrue(self.cards_suit_1[0].is_beaten_by(self.cards_suit_1[1]))
    self.assertFalse(self.cards_suit_1[0].is_beaten_by(self.cards_suit_2[0]))
    self.assertFalse(self.cards_suit_1[0].is_beaten_by(self.cards_suit_2[1]))

    self.assertFalse(self.cards_suit_1[1].is_beaten_by(self.cards_suit_1[0]))
    self.assertFalse(self.cards_suit_1[1].is_beaten_by(self.cards_suit_1[1]))
    self.assertFalse(self.cards_suit_1[1].is_beaten_by(self.cards_suit_2[0]))
    self.assertFalse(self.cards_suit_1[1].is_beaten_by(self.cards_suit_2[1]))

  def test_is_beaten_by_unnenufe(self):
    for card in self.cards_suit_1 + self.cards_suit_2:
      card.set_game_type(GameType.UNNENUFE)

    self.assertFalse(self.cards_suit_1[0].is_beaten_by(self.cards_suit_1[0]))
    self.assertFalse(self.cards_suit_1[0].is_beaten_by(self.cards_suit_1[1]))
    self.assertFalse(self.cards_suit_1[0].is_beaten_by(self.cards_suit_2[0]))
    self.assertFalse(self.cards_suit_1[0].is_beaten_by(self.cards_suit_2[1]))

    self.assertTrue(self.cards_suit_1[1].is_beaten_by(self.cards_suit_1[0]))
    self.assertFalse(self.cards_suit_1[1].is_beaten_by(self.cards_suit_1[1]))
    self.assertFalse(self.cards_suit_1[1].is_beaten_by(self.cards_suit_2[0]))
    self.assertFalse(self.cards_suit_1[1].is_beaten_by(self.cards_suit_2[1]))

  def test_is_beaten_by_trump(self):
    non_trump_1 = Card(Card.SPADES, 1)
    non_trump_2 = Card(Card.CLUBS, 2)
    normal_trump_1 = Card(Card.HEARTS, 0)
    normal_trump_2 = Card(Card.HEARTS, 8)
    nell = Card(Card.HEARTS, 3)
    buur = Card(Card.HEARTS, 5)
    cards = [non_trump_1, non_trump_2, normal_trump_1, normal_trump_2, nell, buur]

    for card in cards:
      card.set_game_type(GameType.TRUMP_HEARTS)
    self.assertFalse(non_trump_1.is_trump)
    self.assertFalse(non_trump_2.is_trump)
    self.assertTrue(normal_trump_1.is_trump)
    self.assertTrue(normal_trump_2.is_trump)
    self.assertTrue(nell.is_trump)
    self.assertTrue(nell.is_nell)
    self.assertTrue(buur.is_trump)
    self.assertTrue(buur.is_buur)

    # buur beats everyone
    self.assertFalse(buur.is_beaten_by(non_trump_1))
    self.assertFalse(buur.is_beaten_by(normal_trump_1))
    self.assertFalse(buur.is_beaten_by(nell))
    self.assertTrue(non_trump_1.is_beaten_by(buur))
    self.assertTrue(normal_trump_1.is_beaten_by(buur))
    self.assertTrue(nell.is_beaten_by(buur))

    # nell beats all non-buurs
    self.assertFalse(nell.is_beaten_by(non_trump_1))
    self.assertFalse(nell.is_beaten_by(normal_trump_1))
    self.assertTrue(nell.is_beaten_by(buur))
    self.assertTrue(non_trump_1.is_beaten_by(nell))
    self.assertTrue(normal_trump_1.is_beaten_by(nell))
    self.assertFalse(buur.is_beaten_by(nell))

    # normal trump beats smaller trump and non-trumps
    self.assertFalse(normal_trump_2.is_beaten_by(non_trump_1))
    self.assertFalse(normal_trump_2.is_beaten_by(normal_trump_1))
    self.assertTrue(normal_trump_2.is_beaten_by(nell))
    self.assertTrue(normal_trump_2.is_beaten_by(buur))
    self.assertTrue(non_trump_1.is_beaten_by(normal_trump_2))
    self.assertTrue(normal_trump_1.is_beaten_by(normal_trump_2))
    self.assertFalse(nell.is_beaten_by(normal_trump_2))
    self.assertFalse(buur.is_beaten_by(normal_trump_2))

    # non-trumps are normal and always lose against trumps
    self.assertFalse(non_trump_1.is_beaten_by(non_trump_2))
    self.assertFalse(non_trump_2.is_beaten_by(non_trump_1))
    self.assertTrue(non_trump_1.is_beaten_by(normal_trump_1))
    self.assertTrue(non_trump_1.is_beaten_by(nell))
    self.assertTrue(non_trump_1.is_beaten_by(buur))
