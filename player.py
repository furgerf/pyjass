#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod

import numpy as np

import utils
from card import Card


class Player(ABC):

  def __init__(self, name, play_best_card, log):
    self._name = name
    self._play_best_card = play_best_card
    self.log = log
    self._hand = None

  @property
  def name(self):
    return self._name

  @property
  def hand(self):
    return self._hand

  @hand.setter
  def hand(self, hand):
    self._hand = sorted(hand, key=lambda c: str(c.suit) + str(c.value))

  def select_card_to_play(self, played_cards, known_cards):
    if played_cards:
      # try to match suit
      valid_cards = list(filter(lambda c: played_cards[0].suit == c.suit, self.hand))
      if not valid_cards:
        # can't match suit, any card is allowed
        valid_cards = self.hand
    else:
      valid_cards = self.hand

    selected_card = self._select_card((valid_cards, played_cards, known_cards))
    self.log.debug("{} selects card {} to play (valid: {})".format(
      self.name, selected_card, utils.format_cards(valid_cards)))

    encoded_player_state = self._encode_cards(played_cards, known_cards)
    if encoded_player_state[selected_card.card_index] != Card.IN_HAND:
      raise ValueError()
    encoded_player_state[selected_card.card_index] = Card.SELECTED

    return selected_card, encoded_player_state

  @abstractmethod
  def _select_card(self, args):
    pass

  @abstractmethod
  def train(self, training_data):
    pass

  @abstractmethod
  def checkpoint(self):
    pass

  def _encode_cards(self, played_cards, known_cards):
    cards = np.array(known_cards, copy=True)
    for pc in played_cards:
      if cards[pc.card_index] != 0:
        raise ValueError()
      cards[pc.card_index] = Card.IN_PLAY
    for hc in self.hand:
      if cards[hc.card_index] != 0:
        raise ValueError()
      cards[hc.card_index] = Card.IN_HAND
    return cards
