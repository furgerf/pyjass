#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from config import Config

import numpy as np

import utils
from const import Const


class Player(ABC):
  """
  Abstract base class of a player providing the interface for the game.
  """

  def __init__(self, name, number, play_best_card, log):
    """
    Creates a new player.

    :name: Name of the player, for display purposes only.
    :number: Number of the player, to determine neighboring players.
    :play_best_card: True if the player should always play the card he thinks is best, may be ignored.
    :log: Logger instance.
    """
    # DON'T store the log or the player can't be serialized
    self._name = name
    self._number = number
    self._play_best_card = play_best_card
    self._hand = None
    log.debug("Created player {}".format(self.name))

  @property
  def name(self):
    """
    Name of the player.
    """
    return self._name

  @property
  def hand(self):
    """
    Current hand cards of the player (list of Card instances).
    """
    return self._hand

  @hand.setter
  def hand(self, hand):
    # sort hand cards, NOTE: might be omitted for performance
    self._hand = sorted(hand, key=lambda c: str(c.suit) + str(c.value))

  def select_card_to_play(self, played_cards, known_cards, game_type, log):
    """
    Have the player select a valid hand card to play.

    :played_cards: The cards that are currently in play.
    :known_cards: Array of all cards encoding the publicly known state.
    :game_type: The current game type.
    :log: Logger instance.

    :returns: The selected card to play and the associated decision state.
    """
    # get all cards that would be valid to play
    # NOTE: this also depends on game type!
    if played_cards:
      # try to match suit
      valid_cards = list(filter(lambda c: played_cards[0].suit == c.suit, self.hand))
      if not valid_cards:
        # can't match suit, any card is allowed
        valid_cards = self.hand
    else:
      valid_cards = self.hand

    # actually select a card
    selected_card = self._select_card((valid_cards, played_cards, known_cards, game_type), log)
    log.debug("{} selects card {} to play (valid: {})".format(
      self.name, selected_card, utils.format_cards(valid_cards)))

    # a decision was made, create the corresponding state
    decision_state = self._encode_current_state(played_cards, known_cards)
    assert decision_state[selected_card.card_index] == Config.ENCODING.card_code_in_hand, \
        "Card to be played must be in the player's hand."
    decision_state[selected_card.card_index] = Config.ENCODING.card_code_selected

    # if requested, sort the decision state
    # afterwards, the encoding of the current state mustn't be modified, all that's missing is cost
    if Config.ENCODING.sort_states:
      decision_state = Player._sort_decision_state(decision_state)

    return selected_card, decision_state

  @abstractmethod
  def _select_card(self, args, log):
    """
    Actual implementation of the decision making.

    :args: Tuple containing a list of all valid cards, a list of all cards that are in play, the
      publicly known state, and the game type.

    :returns: The selected card instance.
    """
    pass

  def select_game_type(self):
    """
    Have the player select the game type.

    :returns: The selected game type.
    """
    assert len(self.hand) == Const.CARDS_PER_PLAYER
    if Config.FORCE_GAME_TYPE:
      return Config.FORCE_GAME_TYPE
    return self._select_game_type()

  @abstractmethod
  def _select_game_type(self):
    """
    Actual implementation of the decision making

    :returns: The selected game type.
    """
    pass

  @abstractmethod
  def train(self, training_data, log):
    """
    Train the player on new data. May be ignored depending on the player implementation.

    :training_data: 2D-numpy-array of training samples.
    :log: Logger instance.
    """
    pass

  @abstractmethod
  def checkpoint(self, current_iteration, total_iterations, log):
    """
    Creates a checkpoint for the player. May be ignored depending on the player implementation.

    :current_iteration: The number of the currently finished iteration.
    :total_iterations: The total number of iterations.
    :log: Logger instance.
    """
    pass

  @abstractmethod
  def get_checkpoint_data(self):
    """
    Retrieve data to write to the checkpoint for the player. May return nothing depending on the
    player implementation.
    """
    pass

  def convert_to_relative(self, player_number):
    """
    Converts the provided absolute player number to a number relative to the current player.

    :player_number: Absolute player number.

    :returns: Relative player number.
    """
    if player_number not in Config.ENCODING.card_code_players:
      # the number isn't actually a player number, return it unchanged
      return player_number
    own_index = Config.ENCODING.card_code_players.index(self._number)
    player_index = Config.ENCODING.card_code_players.index(player_number)
    return Config.ENCODING.card_code_players[(player_index - own_index) % Const.PLAYER_COUNT]

  def _encode_current_state(self, played_cards, known_cards):
    """
    Encodes the current state that is specific to the player.

    :played_cards: The cards that are currently in play.
    :known_cards: Array of all cards encoding the publicly known state.

    :returns: Numpy-array with the current state from the view of the player. This encodes the
      decision state of the player.
    """
    cards = np.array([self.convert_to_relative(card) for card in known_cards]) if \
        Config.ENCODING.relative_player_encoding else np.array(known_cards, copy=True)
    for i, pc in enumerate(played_cards):
      assert cards[pc.card_index] == 0, "Cards in play must've previously been unknown"
      cards[pc.card_index] = Config.ENCODING.card_code_in_play[len(played_cards) - i - 1] if \
          Config.ENCODING.relative_in_play_encoding else Config.ENCODING.card_code_in_play
    for hc in self.hand:
      assert cards[hc.card_index] == 0, "Cards in the player's hand must be unknown"
      cards[hc.card_index] = Config.ENCODING.card_code_in_hand
    return cards

  @staticmethod
  def _sort_decision_state(decision_state):
    """
    Re-arranges the decision state by sorting the suits in a way that the suit itself is irrelevant.

    :decision_state: A list representing the decision state to sort.

    :returns: The list of the sorted decision state.
    """
    assert len(decision_state) == Const.CARDS_PER_PLAYER * Const.PLAYER_COUNT

    # split the decision state into separate lists per suit
    cards_per_suit = [decision_state[Const.CARDS_PER_PLAYER*i:Const.CARDS_PER_PLAYER*(i+1)] \
        for i in range(Const.PLAYER_COUNT)]

    # sort the suits as byte arrays and return the flattened result
    return np.array([item for sublist in sorted(cards_per_suit, key=bytearray) for item in sublist])
