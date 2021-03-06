#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import abstractmethod

import numpy as np

from game_type import GameType
from player import Player


class BaselinePlayer(Player):
  """
  Abstract base class for some baseline players.
  Implements abstact methods that aren't relevant for baseline players.
  """

  def train(self, training_data, log):
    pass

  def checkpoint(self, current_iteration, total_iterations, log):
    pass

  @abstractmethod
  def _select_card(self, args, log):
    pass

  @abstractmethod
  def _select_game_type(self):
    pass

  def get_checkpoint_data(self):
    pass

  @staticmethod
  def _select_random_game_type():
    game_types = list(GameType)
    return game_types[np.random.randint(len(game_types))]

class RandomCardPlayer(BaselinePlayer):
  """
  Player that makes random decisions.
  """

  def __init__(self, name, number, log):
    super(RandomCardPlayer, self).__init__(name, number, [GameType.OBENABE, GameType.UNNENUFE,
      GameType.TRUMP_HEARTS, GameType.TRUMP_SPADES, GameType.TRUMP_DIAMONDS, GameType.TRUMP_CLUBS], log)

  def _select_card(self, args, log):
    valid_cards = args[0]
    return valid_cards[np.random.randint(len(valid_cards))]

  def _select_game_type(self):
    return BaselinePlayer._select_random_game_type()

class HighestCardPlayer(BaselinePlayer):
  """
  Player that selects card with the highest value (not necessarily the best card).
  """

  def __init__(self, name, number, log):
    super(HighestCardPlayer, self).__init__(name, number, [GameType.OBENABE, GameType.UNNENUFE,
      GameType.TRUMP_HEARTS, GameType.TRUMP_SPADES, GameType.TRUMP_DIAMONDS, GameType.TRUMP_CLUBS], log)

  def _select_card(self, args, log):
    game_type = args[3]
    valid_cards = sorted(args[0], key=lambda c: c.value, reverse=(game_type != GameType.UNNENUFE))
    return valid_cards[0]

  def _select_game_type(self):
    return BaselinePlayer._select_random_game_type()


class RulesPlayer(BaselinePlayer):
  """
  Abstract base class for rule-based players. Contains methods that are shared among rule-based players.
  Note that most of these rules rely on playing obenabe!
  """

  @abstractmethod
  def _select_card(self, args, log):
    pass

  @staticmethod
  def _select_best_card_of_first_non_trump_suit(choices):
    """
    Selects the best card of the first suit that isn't the trump suit.
    Note that, counterintuitively, this appears to be better than selecting the "globally" best card.
    Maybe that's because then, the best cards are always played first, and the opponents aren't forced
    to play and lose high-score cards.

    :choices: List of cards that could be selected.

    :returns: Selected card.
    """
    best_card = None
    all_trumps = all(map(lambda card: card.is_trump, choices))
    for card in choices:
      if (best_card is None or (best_card.is_beaten_by(card) and best_card.suit == card.suit)) and \
          (all_trumps or not card.is_trump):
        best_card = card
    return best_card
