#!/usr/bin/env python
# -*- coding: utf-8 -*-

from game_type import GameType


class Card:

  SUITS = "♠♥♦♣"
  VALUES = "6789TJQKA"

  def __init__(self, suit, value):
    self._suit = suit
    self._value = value
    self._icon = Card.VALUES[value] + Card.SUITS[suit]
    self.game_type = None
    self._score = None

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
  def card_index(self):
    """
    Index of the card within an array of all cards.
    """
    return 4*self.value + self.suit

  def __str__(self):
    return self._icon

  def set_game_type(self, game_type):
    """
    Remembers the game type and sets the score of the card depending on the game type (trump).

    :game_type: Type of the game which determines the score of a card.
    """
    self.game_type = game_type
    if game_type == GameType.OBENABE:
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
    elif game_type == GameType.UNNENUFE:
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
    else:
      raise ValueError("Unknown game type: '{}'".format(game_type))
    self._score = scores[self._value]

  def is_beaten_by(self, other_card):
    """
    Determines if the current card is beaten by the other card.

    :other_card: Other card to compare against.

    :returns: True if the other card beats the current card instance.
    """
    if self.game_type == GameType.OBENABE:
      return self.suit == other_card.suit and self.value < other_card.value
    if self.game_type == GameType.UNNENUFE:
      return self.suit == other_card.suit and self.value > other_card.value
    raise ValueError("Unknown game type: '{}'".format(game_type))
