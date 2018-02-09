#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

import utils


class Player():

  def __init__(self, name, log):
    self._name = name
    self._left = None
    self._team = None
    self._right = None
    self._hand = None
    self.log = log

  def set_players(self, left, team, right):
    self._left = left
    self._team = team
    self._right = right

  @property
  def name(self):
    return self._name

  @property
  def hand(self):
    return self._hand

  @hand.setter
  def hand(self, hand):
    self._hand = sorted(hand, key=lambda c: str(c.suit) + str(c.value))

  def select_card_to_play(self, played_cards):
    if played_cards:
      # try to match suit
      valid_cards = list(filter(lambda c: played_cards[0].suit == c.suit, self.hand))
      if not valid_cards:
        # can't match suit, any card is allowed
        valid_cards = self.hand
    else:
      valid_cards = self.hand

    selected_card = self._randomly_select_card(valid_cards)
    self.log.debug("{} selects card {} to play (valid: {})".format(self.name, selected_card, utils.format_cards(valid_cards)))
    return selected_card

  def _randomly_select_card(self, valid_cards):
    return valid_cards[np.random.randint(len(valid_cards))]

