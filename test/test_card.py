#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase

from card import Card
from game_type import GameType


class CardTest(TestCase):
  def setUp(self):
    self.cards_suit_1 = [Card(0, 1), Card(0, 2)]
    self.cards_suit_2 = [Card(1, 1), Card(1, 2)]

  def test_has_worse_value_than_obenabe(self):
    for card in self.cards_suit_1 + self.cards_suit_2:
      card.set_game_type(GameType.OBENABE)

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
