#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import Config
from unittest import TestCase

from card import Card
from encoding import Encoding
from game_type import GameType
from parameterized import parameterized


class CardTest(TestCase):
  # pylint: disable=line-too-long
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

  def test_card_index_by_suit(self):
    Config.ENCODING = Encoding("better", [1, 2, 3, 4], 5, 10, 50, 0, 0, order_value=True, card_index_by_suit=True)
    cards = [
        Card(Card.SPADES, 0), Card(Card.SPADES, Card.VALUE_NELL), Card(Card.SPADES, Card.VALUE_BUUR), Card(Card.SPADES, 8),
        Card(Card.HEARTS, 0), Card(Card.HEARTS, Card.VALUE_NELL), Card(Card.HEARTS, Card.VALUE_BUUR), Card(Card.HEARTS, 8),
        Card(Card.DIAMONDS, 0), Card(Card.DIAMONDS, Card.VALUE_NELL), Card(Card.DIAMONDS, Card.VALUE_BUUR), Card(Card.DIAMONDS, 8),
        Card(Card.CLUBS, 0), Card(Card.CLUBS, Card.VALUE_NELL), Card(Card.CLUBS, Card.VALUE_BUUR), Card(Card.CLUBS, 8)
        ]
    for card in cards:
      card.set_game_type(GameType.TRUMP_DIAMONDS)

    # SPADES: not trump, doesn't get reshuffled
    self.assertEqual(0, cards[0].card_index)
    self.assertEqual(3, cards[1].card_index)
    self.assertEqual(5, cards[2].card_index)
    self.assertEqual(8, cards[3].card_index)

    # HEARTS: not trump, doesn't get reshuffled
    self.assertEqual(0+9, cards[4].card_index)
    self.assertEqual(3+9, cards[5].card_index)
    self.assertEqual(5+9, cards[6].card_index)
    self.assertEqual(8+9, cards[7].card_index)

    # DIAMONDS: trump, gets reshuffled
    self.assertEqual(0+18, cards[8].card_index)
    self.assertEqual(7+18, cards[9].card_index)
    self.assertEqual(8+18, cards[10].card_index)
    self.assertEqual(6+18, cards[11].card_index)

    # CLUBS: not trump, doesn't get reshuffled
    self.assertEqual(0+27, cards[12].card_index)
    self.assertEqual(3+27, cards[13].card_index)
    self.assertEqual(5+27, cards[14].card_index)
    self.assertEqual(8+27, cards[15].card_index)

  def test_card_index_by_value(self):
    Config.ENCODING = Encoding("better", [1, 2, 3, 4], 5, 10, 50, 0, 0, order_value=True, card_index_by_suit=False)
    cards = [
        Card(Card.SPADES, 0), Card(Card.SPADES, Card.VALUE_NELL), Card(Card.SPADES, Card.VALUE_BUUR), Card(Card.SPADES, 8),
        Card(Card.HEARTS, 0), Card(Card.HEARTS, Card.VALUE_NELL), Card(Card.HEARTS, Card.VALUE_BUUR), Card(Card.HEARTS, 8),
        Card(Card.DIAMONDS, 0), Card(Card.DIAMONDS, Card.VALUE_NELL), Card(Card.DIAMONDS, Card.VALUE_BUUR), Card(Card.DIAMONDS, 8),
        Card(Card.CLUBS, 0), Card(Card.CLUBS, Card.VALUE_NELL), Card(Card.CLUBS, Card.VALUE_BUUR), Card(Card.CLUBS, 8)
        ]
    for card in cards:
      card.set_game_type(GameType.TRUMP_DIAMONDS)

    # SPADES: not trump, doesn't get reshuffled
    self.assertEqual(0, cards[0].card_index)
    self.assertEqual(12, cards[1].card_index)
    self.assertEqual(20, cards[2].card_index)
    self.assertEqual(32, cards[3].card_index)

    # HEARTS: not trump, doesn't get reshuffled
    self.assertEqual(1, cards[4].card_index)
    self.assertEqual(13, cards[5].card_index)
    self.assertEqual(21, cards[6].card_index)
    self.assertEqual(33, cards[7].card_index)

    # DIAMONDS: trump, gets reshuffled
    self.assertEqual(2, cards[8].card_index)
    self.assertEqual(14+16, cards[9].card_index)
    self.assertEqual(22+12, cards[10].card_index)
    self.assertEqual(34-8, cards[11].card_index)

    # CLUBS: not trump, doesn't get reshuffled
    self.assertEqual(3, cards[12].card_index)
    self.assertEqual(15, cards[13].card_index)
    self.assertEqual(23, cards[14].card_index)
    self.assertEqual(35, cards[15].card_index)
