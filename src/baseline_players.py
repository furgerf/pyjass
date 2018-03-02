#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import abstractmethod

import numpy as np

from player import Player


class BaselinePlayer(Player):
  def train(self, training_data):
    pass

  def checkpoint(self, current_iteration, total_iterations):
    pass

  @abstractmethod
  def _select_card(self, args):
    pass

  def get_checkpoint_data(self):
    return None


class RandomCardPlayer(BaselinePlayer):
  def _select_card(self, args):
    valid_cards = args[0]
    return valid_cards[np.random.randint(len(valid_cards))]


class HighestCardPlayer(BaselinePlayer):
  def _select_card(self, args):
    valid_cards = args[0]
    return valid_cards[-1]


class SimpleRulesPlayer(BaselinePlayer):
  @staticmethod
  def _select_best_card(choices):
    best_card = choices[0]
    for card in choices:
      if best_card.is_beaten_by(card):
        best_card = card
    return best_card

  @staticmethod
  def _select_worst_card(choices):
    worst_card = choices[0]
    for card in choices:
      # compare value because that also works if the player can't match suit
      if card.value < worst_card.value:
        worst_card = card
    return worst_card

  # pylint: disable=too-many-return-statements
  def _select_card(self, args):
    valid_cards, played_cards, _ = args

    if len(played_cards) == 0: # pylint: disable=len-as-condition
      # first player: choose best card
      self.log.debug("First player choses the card with highest value")
      return SimpleRulesPlayer._select_best_card(valid_cards)

    if len(played_cards) == 1:
      # second player: check if he can beat the first player
      beating_cards = list(filter(played_cards[0].is_beaten_by, valid_cards))
      if beating_cards:
        # first player can be beat: play worst beating card
        best_card = SimpleRulesPlayer._select_worst_card(beating_cards)
        self.log.debug("Second player can beat first card, selecting worst beating: {}".format(best_card))
        return best_card
      # first player can't be beat: play worst card
      worst_card = SimpleRulesPlayer._select_worst_card(valid_cards)
      self.log.debug("Second player can't beat first one or match suit, selecting lowest value: {}"
          .format(worst_card))
      return worst_card

    if len(played_cards) == 2:
      # third player: check if the round currently belongs to the team
      if played_cards[1].is_beaten_by(played_cards[0]):
        # the round is the first player's: play the worst card
        worst_card = SimpleRulesPlayer._select_worst_card(valid_cards)
        self.log.debug("Third player plays card with lowest value because round belongs to team: {}"
            .format(worst_card))
        return worst_card
      # the round isn't the first player's: check if he can beat player 2
      beating_cards = list(filter(played_cards[1].is_beaten_by, valid_cards))
      if beating_cards:
        # first player can be beat: play worst beating card
        best_card = SimpleRulesPlayer._select_worst_card(beating_cards)
        self.log.debug("Third player can beat second card, selecting worst beating: {}".format(best_card))
        return best_card
      # first player can't be beat: play worst card
      worst_card = SimpleRulesPlayer._select_worst_card(valid_cards)
      self.log.debug("Third player can't beat second one or match suit, selecting lowest value: {}"
          .format(worst_card))
      return worst_card

    # fourth player: check if the round currently belongs to the team
    if played_cards[0].is_beaten_by(played_cards[1]) and played_cards[2].is_beaten_by(played_cards[1]):
      # the round is the second player's: play the worst card
      worst_card = SimpleRulesPlayer._select_worst_card(valid_cards)
      self.log.debug("Fourth player plays card with lowest value because round belongs to team: {}"
          .format(worst_card))
      return worst_card
    # the round isn't the second player's: check if the round can be won
    beating_cards = list(filter(lambda my_card:
      played_cards[0].is_beaten_by(my_card) and played_cards[2].is_beaten_by(my_card), valid_cards))
    if beating_cards:
      # the round can be won, play WORST beating card
      worst_card = SimpleRulesPlayer._select_worst_card(beating_cards)
      self.log.debug("Fourth player can win round, selecting worst: {}".format(worst_card))
      return worst_card
    # the round can't be won: play worst card
    worst_card = SimpleRulesPlayer._select_worst_card(valid_cards)
    self.log.debug("Fourth player can't win round, selecting lowest value: {}".format(worst_card))
    return worst_card
