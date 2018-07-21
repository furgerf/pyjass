#!/usr/bin/env python
# -*- coding: utf-8 -*-

from baseline_players import RulesPlayer
from card import Card
from game_type import GameType


class SimpleRulesPlayer(RulesPlayer):
  """
  Player that selects cards based on a few simple rules.
  Only the current round is considered, no memory of previous rounds.
  """

  @staticmethod
  def _select_worst_card(choices):
    """
    Selects the card with the lowest value among the choices.

    :choices: List of cards that could be selected.

    :returns: Selected card.
    """
    worst_card = choices[0]
    for card in choices:
      # compare value because that also works if the player can't match suit
      if card.has_worse_value_than(worst_card):
        worst_card = card
    return worst_card

  # pylint: disable=too-many-return-statements
  def _select_card(self, args, log):
    valid_cards, played_cards, _, _ = args

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

  def _select_game_type(self):
    #  decide between obenabe and unnenufe by checking whether there are more cards above or below 10 in the hand
    high_card_count = len(list(filter(lambda card: card.value > int(len(Card.VALUES)/2), self.hand)))
    low_card_count = len(list(filter(lambda card: card.value < int(len(Card.VALUES)/2), self.hand)))
    return GameType.OBENABE if high_card_count >= low_card_count else GameType.UNNENUFE