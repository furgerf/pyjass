#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import Config

from const import Const
from game_type import GameType


class Card:

  SUITS = "♠♥♦♣"
  SPADES = 0
  HEARTS = 1
  DIAMONDS = 2
  CLUBS = 3

  TRUMP_GAME_TYPE_TO_SUIT = {
      GameType.TRUMP_SPADES: SPADES,
      GameType.TRUMP_HEARTS: HEARTS,
      GameType.TRUMP_DIAMONDS: DIAMONDS,
      GameType.TRUMP_CLUBS: CLUBS
      }

  VALUES = "6789TJQKA"

  VALUE_BUUR = 5
  VALUE_NELL = 3

  def __init__(self, suit, value):
    self._suit = suit
    self._value = value
    self._icon = Card.VALUES[value] + Card.SUITS[suit]
    self._game_type = None
    self._score = None
    self._is_trump = None

  @property
  def suit(self):
    """
    Suit of the card, integer from 0 to 3.
    """
    return self._suit

  @property
  def value(self):
    """
    Value of the card (order within the suit), integer from 0 to 8.
    """
    return self._value

  @property
  def score(self):
    """
    Number of points gained by winnning this card, the value depends on the game type.
    """
    return self._score

  @property
  def is_trump(self):
    """
    True if the card is a trump card.
    """
    return self._is_trump

  @property
  def is_buur(self):
    """
    True if the card is the buur (trump J).
    """
    return self.is_trump and self.value == Card.VALUE_BUUR

  @property
  def is_nell(self):
    """
    True if the card is the nell (trump 9).
    """
    return self.is_trump and self.value == Card.VALUE_NELL

  @property
  def card_index(self):
    """
    Index of the card within an array of all cards.
    """
    if Config.ENCODING.card_index_by_suit:
      return self.value + self.suit * Const.CARDS_PER_SUIT
    return Const.SUIT_COUNT * self.value + self.suit

  def __str__(self):
    return self._icon

  def __eq__(self, other):
    return isinstance(other, Card) and self.suit == other.suit and self.value == other.value

  def set_game_type(self, game_type):
    """
    Remembers the game type and sets the score of the card depending on the game type (trump).

    :game_type: Type of the game which determines the score of a card.
    """
    self._game_type = game_type
    self._is_trump = self.suit == Card.TRUMP_GAME_TYPE_TO_SUIT.get(self._game_type)
    if self._game_type == GameType.OBENABE:
      scores = {
          0: 0,
          1: 0,
          2: 8,
          3: 0,
          4: 10,
          5: 2,
          6: 3,
          7: 4,
          8: 11
          }
    elif self._game_type == GameType.UNNENUFE:
      scores = {
          0: 11,
          1: 0,
          2: 8,
          3: 0,
          4: 10,
          5: 2,
          6: 3,
          7: 4,
          8: 0
          }
    elif self._game_type.is_trump_game_type:
      scores = {
          0: 0,
          1: 0,
          2: 0,
          3: 14,
          4: 10,
          5: 20,
          6: 3,
          7: 4,
          8: 11
          } if self._is_trump else {
              0: 0,
              1: 0,
              2: 0,
              3: 0,
              4: 10,
              5: 2,
              6: 3,
              7: 4,
              8: 11
              }
    else:
      raise ValueError("Unknown game type: '{}'".format(self._game_type))
    self._score = scores[self._value]

  def is_beaten_by(self, other_card):
    # pylint: disable=too-many-return-statements
    """
    Determines if the current card is beaten by the other card.

    :other_card: Other card to compare against.

    :returns: True if the other card beats the current card instance.
    """
    if self._game_type in [GameType.OBENABE, GameType.UNNENUFE]:
      return self.suit == other_card.suit and self.has_worse_value_than(other_card)
    if self._game_type.is_trump_game_type:
      if self.is_trump ^ other_card.is_trump:
        # only one of the cards is trump
        return other_card.is_trump
      if not self.is_trump:
        # none of the cards is trump
        return self.suit == other_card.suit and self.has_worse_value_than(other_card)
      # both are trump
      if self.is_buur:
        return False
      if other_card.is_buur:
        return True
      if self.is_nell:
        return False
      if other_card.is_nell:
        return True
      return self.has_worse_value_than(other_card)
    raise ValueError("Unknown game type: '{}'".format(self._game_type))

  def has_worse_value_than(self, other_card):
    """
    Determines if the current card has a worse value than the other card.

    :other_card: Other card to compare against.

    :returns: True if the other card has a better value than the current card instance.
    """
    if self._game_type == GameType.OBENABE or self._game_type.is_trump_game_type:
      return self.value < other_card.value
    if self._game_type == GameType.UNNENUFE:
      return self.value > other_card.value
    raise ValueError("Unknown game type: '{}'".format(self._game_type))
