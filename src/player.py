#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from config import Config

import numpy as np

import utils
from const import Const
from game_type import GameType


class Player(ABC):
  """
  Abstract base class of a player providing the interface for the game.
  """

  def __init__(self, name, number, known_game_types, log):
    """
    Creates a new player.

    :name: Name of the player, for display purposes only.
    :number: Number of the player, to determine neighboring players.
    :log: Logger instance.
    """
    # DON'T store the log or the player can't be serialized
    self._name = name
    self._number = number
    self._known_game_types = known_game_types
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

  def knows_game_type(self, game_type):
    """
    Check if the player knows the queried game type.

    :game_type: The game type to check.

    :returns: True if the player knows the game type.
    """
    return game_type in self._known_game_types

  def knows_same_game_types_as(self, other_player):
    """
    Checks if the player knows the same game types as another player.

    :other_player: The other player to compare the known game types against.

    :returns True if both players know the same game types.
    """
    # pylint: disable=protected-access
    return set(self._known_game_types) == set(other_player._known_game_types)

  def select_card_to_play(self, played_cards, known_cards, game_type, log):
    """
    Have the player select a valid hand card to play.

    :played_cards: The cards that are currently in play.
    :known_cards: Array of all cards encoding the publicly known state.
    :game_type: The current game type.
    :log: Logger instance.

    :returns: The selected card to play and the associated decision state.
    """
    assert self.knows_game_type(game_type)

    # get all cards that would be valid to play
    valid_cards = self.get_valid_cards_to_play(played_cards, game_type)

    # actually select a card
    selected_card = self._select_card((valid_cards, played_cards, known_cards, game_type), log)
    log.debug("{} selects card {} to play (valid: {} - invalid: {})".format(
      self.name, selected_card, utils.format_cards(valid_cards), \
          utils.format_cards([card for card in self.hand if card not in valid_cards])))

    # a decision was made, create the corresponding state
    decision_state = self._encode_current_state(played_cards, known_cards)
    assert decision_state[selected_card.card_index] in [Config.ENCODING.card_code_in_hand, \
        Config.ENCODING.card_code_in_hand + Config.ENCODING.trump_code_offset], \
        "Card to be played must be in the player's hand."
    decision_state[selected_card.card_index] = Config.ENCODING.card_code_selected + \
        (Config.ENCODING.trump_code_offset if selected_card.is_trump else 0)

    # if requested, sort the decision state
    # afterwards, the encoding of the current state mustn't be modified, all that's missing is cost
    if Config.ENCODING.sort_states:
      decision_state = Player._sort_decision_state(decision_state, Config.ENCODING.card_index_by_suit)

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

  def get_valid_cards_to_play(self, played_cards, game_type):
    """
    Get all cards in the player's hand that would be valid to play.

    :played_cards: The cards that are currently in play.
    :game_type: The current game type.

    :returns: A list of all cards that the player is allowed to play.
    """
    if not played_cards:
      # the first player can always choose from all cards
      return self.hand

    if game_type in [GameType.OBENABE, GameType.UNNENUFE]:
      # try to match suit
      valid_cards = list(filter(lambda c: played_cards[0].suit == c.suit, self.hand))
      # all cards are valid if unable to match suit
      return valid_cards or self.hand
    if game_type.is_trump_game_type:
      # try to match suit
      valid_cards = list(filter(lambda c: played_cards[0].suit == c.suit, self.hand))
      # prepare trump-related things
      played_trumps = list(filter(lambda c: c.is_trump, played_cards))
      best_trump = played_trumps[0] if played_trumps else None
      for played_trump in played_trumps:
        if best_trump.is_beaten_by(played_trump):
          best_trump = played_trump
      non_undertrumping_trumps = list(filter(lambda c: c.is_trump and \
          (best_trump is None or best_trump.is_beaten_by(c)), self.hand))
      if not valid_cards:
        # all non-undertrumping cards are valid if unable to match suit and non-trump cards are in the hand
        if all(map(lambda c: c.is_trump, self.hand)):
          return self.hand
        return list(filter(lambda c: not c.is_trump or c in non_undertrumping_trumps, self.hand))
      if played_cards[0].is_trump:
        # if the only valid (trump) card is the buur, all cards are valid, otherwise all valid (trump) cards are
        return self.hand if len(valid_cards) == 1 and valid_cards[0].is_buur else valid_cards
      # besides matching suit, non-undertrumping trumps can also be played
      valid_cards.extend(non_undertrumping_trumps)
      return valid_cards
    raise ValueError("Unknown game type: '{}'".format(GameType.name))

  def select_game_type(self):
    """
    Have the player select the game type.

    :returns: The selected game type.
    """
    assert len(self.hand) == Const.CARDS_PER_PLAYER, "only select game type when no cards are played"
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
    if player_number == 0:
      # unknown cards stay unknown
      return 0
    # all other known cards must have been previously played by some player
    # check if the card code is for a trump card of a player
    card_is_trump = Config.ENCODING.trump_code_offset and player_number in \
        np.array(Config.ENCODING.card_code_players) + Config.ENCODING.trump_code_offset
    if card_is_trump:
      player_number -= Config.ENCODING.trump_code_offset
    # after accounting for trump cards, the card's code must be a player's
    assert player_number in Config.ENCODING.card_code_players
    own_index = Config.ENCODING.card_code_players.index(self._number)
    player_index = Config.ENCODING.card_code_players.index(player_number)
    return Config.ENCODING.card_code_players[(player_index - own_index) % Const.PLAYER_COUNT] + \
        (Config.ENCODING.trump_code_offset if card_is_trump else 0)

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
      cards[pc.card_index] = (Config.ENCODING.card_code_in_play[len(played_cards) - i - 1] if \
          Config.ENCODING.relative_in_play_encoding else Config.ENCODING.card_code_in_play) + \
          (Config.ENCODING.trump_code_offset if pc.is_trump else 0)
    for hc in self.hand:
      assert cards[hc.card_index] == 0, "Cards in the player's hand must be unknown"
      cards[hc.card_index] = Config.ENCODING.card_code_in_hand + \
          (Config.ENCODING.trump_code_offset if hc.is_trump else 0)
    return cards

  @staticmethod
  def _sort_decision_state(decision_state, cards_by_suit):
    """
    Re-arranges the decision state by sorting the suits in a way that the suit itself is irrelevant.

    :decision_state: A list representing the decision state to sort.
    :cards_by_suit: True if the decision state represents cards that are ordered by suit, false if
                    they're ordered by value.

    :returns: The list of the sorted decision state.
    """
    assert len(decision_state) == Const.CARDS_PER_PLAYER * Const.PLAYER_COUNT

    # split the decision state into separate lists per suit
    if cards_by_suit:
      cards_per_suit = [decision_state[Const.CARDS_PER_SUIT*i:Const.CARDS_PER_SUIT*(i+1)] \
          for i in range(Const.SUIT_COUNT)]
    else:
      cards_per_suit = [decision_state[i::Const.SUIT_COUNT] for i in range(Const.SUIT_COUNT)]

    # sort the suits as byte arrays
    sorted_suits = sorted(cards_per_suit, key=bytearray)

    # if the cards are ordered by value, the suit lists need to be zipped to re-establish that order
    if not cards_by_suit:
      sorted_suits = zip(*sorted_suits)

    # flatten and return the sorted decision state
    return np.array(utils.flatten(sorted_suits))
