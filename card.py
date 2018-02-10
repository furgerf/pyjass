#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Card():

  SUITS = "♠♥♦♣"
  VALUES = "6789TJQKA"

  ICONS = "🂦🂶🃆🃖" + \
          "🂧🂷🃇🃗" + \
          "🂨🂸🃈🃘" + \
          "🂩🂹🃉🃙" + \
          "🂪🂺🃊🃚" + \
          "🂫🂻🃋🃛" + \
          "🂭🂽🃍🃝" + \
          "🂮🂾🃎🃞" + \
          "🂡🂱🃁🃑 "

  IN_PLAY = 5
  IN_HAND = 6
  SELECTED = 7

  def __init__(self, suit, value):
    self._suit = suit
    self._value = value
    self._score = -12345
    # self._icon = Card.ICONS[4*value+suit]
    self._icon = Card.VALUES[value] + Card.SUITS[suit]

  @property
  def suit(self):
    return self._suit

  @property
  def value(self):
    return self._value

  @property
  def score(self):
    return self._score

  @property
  def card_index(self):
    return 4*self.value + self.suit

  def __str__(self):
    return self._icon

  def set_score(self, trump):
    if trump == "obenabe":
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

    self._score = scores[self._value]

  def is_beaten_by(self, other_card):
    return self.suit == other_card.suit and self.value < other_card.value

