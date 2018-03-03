#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from config import Config

import numpy as np

import utils


class Player(ABC):

  def __init__(self, name, play_best_card, log):
    # DON'T store log
    self._name = name
    self._play_best_card = play_best_card
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

  def select_card_to_play(self, played_cards, known_cards, log):
    if played_cards:
      # try to match suit
      valid_cards = list(filter(lambda c: played_cards[0].suit == c.suit, self.hand))
      if not valid_cards:
        # can't match suit, any card is allowed
        valid_cards = self.hand
    else:
      valid_cards = self.hand

    selected_card = self._select_card((valid_cards, played_cards, known_cards), log)
    log.debug("{} selects card {} to play (valid: {})".format(
      self.name, selected_card, utils.format_cards(valid_cards)))

    encoded_player_state = self._encode_cards(played_cards, known_cards)
    if encoded_player_state[selected_card.card_index] != Config.ENCODING.card_code_in_hand:
      raise ValueError()
    encoded_player_state[selected_card.card_index] = Config.ENCODING.card_code_selected

    return selected_card, encoded_player_state

  @abstractmethod
  def _select_card(self, args, log):
    pass

  @abstractmethod
  def train(self, training_data, log):
    pass

  @abstractmethod
  def checkpoint(self, current_iteration, total_iterations):
    pass

  @abstractmethod
  def get_checkpoint_data(self):
    pass

  def _encode_cards(self, played_cards, known_cards):
    cards = np.array(known_cards, copy=True)
    for pc in played_cards:
      if cards[pc.card_index] != 0:
        raise ValueError()
      cards[pc.card_index] = Config.ENCODING.card_code_in_play
    for hc in self.hand:
      if cards[hc.card_index] != 0:
        raise ValueError()
      cards[hc.card_index] = Config.ENCODING.card_code_in_hand
    return cards
