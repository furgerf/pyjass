#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import abstractmethod

import numpy as np

from card import Card
from player import Player


class BaselinePlayer(Player):
  def train(self, training_data, log):
    pass

  def checkpoint(self, current_iteration, total_iterations, log):
    pass

  @abstractmethod
  def _select_card(self, args, log):
    pass

  def get_checkpoint_data(self):
    return None


class RandomCardPlayer(BaselinePlayer):
  def _select_card(self, args, log):
    valid_cards = args[0]
    return valid_cards[np.random.randint(len(valid_cards))]


class HighestCardPlayer(BaselinePlayer):
  def _select_card(self, args, log):
    valid_cards = args[0]
    return valid_cards[-1]


class RulesPlayer(BaselinePlayer):
  @abstractmethod
  def _select_card(self, args, log):
    pass

  @staticmethod
  def _select_best_card_of_first_suit(choices):
    best_card = choices[0]
    for card in choices:
      if best_card.is_beaten_by(card):
        best_card = card
    return best_card


class SimpleRulesPlayer(RulesPlayer):
  @staticmethod
  def _select_worst_card(choices):
    worst_card = choices[0]
    for card in choices:
      # compare value because that also works if the player can't match suit
      if card.value < worst_card.value:
        worst_card = card
    return worst_card

  # pylint: disable=too-many-return-statements
  def _select_card(self, args, log):
    valid_cards, played_cards, _ = args

    if len(played_cards) == 0: # pylint: disable=len-as-condition
      # first player: choose best card
      log.debug("First player choses the card with highest value")
      return RulesPlayer._select_best_card_of_first_suit(valid_cards)

    if len(played_cards) == 1:
      # second player: check if he can beat the first player
      beating_cards = list(filter(played_cards[0].is_beaten_by, valid_cards))
      if beating_cards:
        # first player can be beat: play worst beating card
        best_card = SimpleRulesPlayer._select_worst_card(beating_cards)
        log.debug("Second player can beat first card, selecting worst beating: {}".format(best_card))
        return best_card
      # first player can't be beat: play worst card
      worst_card = SimpleRulesPlayer._select_worst_card(valid_cards)
      log.debug("Second player can't beat first one or match suit, selecting lowest value: {}"
          .format(worst_card))
      return worst_card

    if len(played_cards) == 2:
      # third player: check if the round currently belongs to the team
      if played_cards[1].is_beaten_by(played_cards[0]):
        # the round is the first player's: play the worst card
        worst_card = SimpleRulesPlayer._select_worst_card(valid_cards)
        log.debug("Third player plays card with lowest value because round belongs to team: {}"
            .format(worst_card))
        return worst_card
      # the round isn't the first player's: check if he can beat player 2
      beating_cards = list(filter(played_cards[1].is_beaten_by, valid_cards))
      if beating_cards:
        # first player can be beat: play worst beating card
        best_card = SimpleRulesPlayer._select_worst_card(beating_cards)
        log.debug("Third player can beat second card, selecting worst beating: {}".format(best_card))
        return best_card
      # first player can't be beat: play worst card
      worst_card = SimpleRulesPlayer._select_worst_card(valid_cards)
      log.debug("Third player can't beat second one or match suit, selecting lowest value: {}"
          .format(worst_card))
      return worst_card

    # fourth player: check if the round currently belongs to the team
    if played_cards[0].is_beaten_by(played_cards[1]) and played_cards[2].is_beaten_by(played_cards[1]):
      # the round is the second player's: play the worst card
      worst_card = SimpleRulesPlayer._select_worst_card(valid_cards)
      log.debug("Fourth player plays card with lowest value because round belongs to team: {}"
          .format(worst_card))
      return worst_card
    # the round isn't the second player's: check if the round can be won
    beating_cards = list(filter(lambda my_card:
      played_cards[0].is_beaten_by(my_card) and played_cards[2].is_beaten_by(my_card), valid_cards))
    if beating_cards:
      # the round can be won, play WORST beating card
      worst_card = SimpleRulesPlayer._select_worst_card(beating_cards)
      log.debug("Fourth player can win round, selecting worst: {}".format(worst_card))
      return worst_card
    # the round can't be won: play worst card
    worst_card = SimpleRulesPlayer._select_worst_card(valid_cards)
    log.debug("Fourth player can't win round, selecting lowest value: {}".format(worst_card))
    return worst_card


class BetterRulesPlayer(RulesPlayer):
  HIGH_SCORE_LOW_VALUE_CARDS = [2, 4]

  # NOTE: these rules rely on playing obenabe!

  @staticmethod
  def _get_counts_per_suit(cards):
    return [len(list(filter(lambda card: card.suit == suit, cards))) for suit in range(len(Card.SUITS))]

  @staticmethod
  def _select_high_scoring_or_useless_card(choices):
    # get high-scoring cards; sort them by score descending
    high_scoring = list(sorted(filter(
      lambda card: card.value in BetterRulesPlayer.HIGH_SCORE_LOW_VALUE_CARDS, choices),
      key=lambda card: card.score, reverse=True))

    # we have no high-scoring cards, return worst card
    if not high_scoring:
      return BetterRulesPlayer._select_useless_card(choices)

    # we do have high-scoring cards, return the card with max score with number of cards per suit as tiebreaker
    suit_counts = BetterRulesPlayer._get_counts_per_suit(choices)
    card_to_play = high_scoring[0]
    for card in high_scoring:
      if card.score >= card_to_play.score and suit_counts[card.suit] < suit_counts[card_to_play.suit]:
        card_to_play = card
    return card_to_play

  @staticmethod
  def _select_useless_card(choices):
    # separating the low-scoring cards doesn't seem to help...

    suit_counts = BetterRulesPlayer._get_counts_per_suit(choices)
    card_to_play = choices[0]
    for card in choices:
      suit_count_diff = suit_counts[card.suit] - suit_counts[card_to_play.suit]
      value_diff = card.value - card_to_play.value
      score_diff = card.score - card_to_play.score

      # this weighting seems to be work best...
      if (1*value_diff) + (1*score_diff) + (3*suit_count_diff) < 0:
        card_to_play = card
    return card_to_play

  # pylint: disable=too-many-return-statements
  def _select_card(self, args, log):
    valid_cards, played_cards, _ = args

    if len(played_cards) == 0: # pylint: disable=len-as-condition
      # first player: choose best card
      log.debug("First player choses the card with highest value")
      return RulesPlayer._select_best_card_of_first_suit(valid_cards)

    if len(played_cards) == 1:
      # second player: check if he can beat the first player
      beating_cards = list(filter(played_cards[0].is_beaten_by, valid_cards))
      if beating_cards:
        # first player can be beat: play worst beating card
        best_card = BetterRulesPlayer._select_useless_card(beating_cards)
        log.debug("Second player can beat first card, selecting worst beating: {}".format(best_card))
        return best_card
      # first player can't be beat: play worst card
      worst_card = BetterRulesPlayer._select_useless_card(valid_cards)
      log.debug("Second player can't beat first one or match suit, selecting lowest value: {}"
          .format(worst_card))
      return worst_card

    if len(played_cards) == 2:
      # third player: check if the round currently belongs to the team
      if played_cards[1].is_beaten_by(played_cards[0]):
        # the round is the first player's: play the highest-score or worst card
        worst_card = BetterRulesPlayer._select_high_scoring_or_useless_card(valid_cards)
        log.debug("Third player plays card with high score or lowest value because round belongs to team: {}"
            .format(worst_card))
        return worst_card
      # the round isn't the first player's: check if he can beat player 2
      beating_cards = list(filter(played_cards[1].is_beaten_by, valid_cards))
      if beating_cards:
        # first player can be beat: play worst beating card
        best_card = BetterRulesPlayer._select_high_scoring_or_useless_card(beating_cards) # NOTE: try both
        log.debug("Third player can beat second card, selecting worst beating: {}".format(best_card))
        return best_card
      # first player can't be beat: play worst card
      worst_card = BetterRulesPlayer._select_useless_card(valid_cards)
      log.debug("Third player can't beat second one or match suit, selecting lowest value: {}"
          .format(worst_card))
      return worst_card

    # fourth player: check if the round currently belongs to the team
    if played_cards[0].is_beaten_by(played_cards[1]) and played_cards[2].is_beaten_by(played_cards[1]):
      # the round is the second player's: play the highest-score or worst card
      worst_card = BetterRulesPlayer._select_high_scoring_or_useless_card(valid_cards)
      log.debug("Fourth player plays card with high score or lowest value because round belongs to team: {}"
          .format(worst_card))
      return worst_card
    # the round isn't the second player's: check if the round can be won
    beating_cards = list(filter(lambda my_card:
      played_cards[0].is_beaten_by(my_card) and played_cards[2].is_beaten_by(my_card), valid_cards))
    if beating_cards:
      # the round can be won, play WORST beating card (but prefer high-scoring cards)
      worst_card = BetterRulesPlayer._select_high_scoring_or_useless_card(beating_cards)
      log.debug("Fourth player can win round, selecting high score or worst: {}".format(worst_card))
      return worst_card
    # the round can't be won: play worst card
    worst_card = BetterRulesPlayer._select_useless_card(valid_cards)
    log.debug("Fourth player can't win round, selecting lowest value: {}".format(worst_card))
    return worst_card
