#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from config import Config

import numpy as np

import utils
from const import Const


class Player(ABC):

  def __init__(self, name, number, play_best_card, log):
    # DON'T store the log
    self._name = name
    self._number = number
    self._play_best_card = play_best_card
    self._hand = None
    log.debug("Created player {}".format(self.name))

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
    assert encoded_player_state[selected_card.card_index] == Config.ENCODING.card_code_in_hand, \
        "Card to be played must be in the player's hand."
    encoded_player_state[selected_card.card_index] = Config.ENCODING.card_code_selected

    return selected_card, encoded_player_state

  @abstractmethod
  def _select_card(self, args, log):
    pass

  @abstractmethod
  def train(self, training_data, log):
    pass

  @abstractmethod
  def checkpoint(self, current_iteration, total_iterations, log):
    pass

  @abstractmethod
  def get_checkpoint_data(self):
    pass

  def convert_to_relative(self, index):
    if index == 0 or index in Config.ENCODING.card_code_players:
      return index
    return Config.ENCODING[(index - self._number) % Const.PLAYER_COUNT]

  def _encode_cards(self, played_cards, known_cards):
    cards = np.array([self.convert_to_relative(card) for card in known_cards]) if \
        Config.ENCODING.relative_player_encoding else np.array(known_cards, copy=True)
    for pc in played_cards:
      assert cards[pc.card_index] == 0, "Cards in play must've previously been unknown"
      cards[pc.card_index] = Config.ENCODING.card_code_in_play
    for hc in self.hand:
      assert cards[hc.card_index] == 0, "Cards in the player's hand must be unknown"
      cards[hc.card_index] = Config.ENCODING.card_code_in_hand
    return cards
