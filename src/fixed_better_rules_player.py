#!/usr/bin/env python
# -*- coding: utf-8 -*-

from baseline_players import RulesPlayer
from card import Card
from game_type import GameType


class FixedBetterRulesPlayer(RulesPlayer):
  """
  Player that selects cards based on some improved rules.
  Only the current round is considered, no memory of previous rounds.
  """

  # early means when there's still an opponent left
  STECHEN_THRESHOLD_EARLY = 11 # more than a banner
  STECHEN_THRESHOLD_LATE = 5 # more than a king

  def __init__(self, name, number, log):
    super(FixedBetterRulesPlayer, self).__init__(name, number, [GameType.OBENABE, GameType.UNNENUFE,
        GameType.TRUMP_HEARTS, GameType.TRUMP_SPADES, GameType.TRUMP_DIAMONDS, GameType.TRUMP_CLUBS], log)

  @staticmethod
  def _get_counts_per_suit(cards):
    """
    Calculates the counts per suit among the provided cards.

    :cards: The cards of which to count the suits.

    :returns: List where each item is the number of cards of the corresponding suit.
    """
    # pylint: disable=cell-var-from-loop
    return [len(list(filter(lambda card: card.suit == suit, cards))) for suit in range(len(Card.SUITS))]

  @staticmethod
  def _select_trump_card(choices, has_opponent_left, game_type):
    """
    Selects one of the trump cards for a stich.

    :choices: List of cards that could be selected.
    :has_opponent_left: True if there is still another opponent.
    :game_type: Type of the game.

    :returns: Selected card.
    """
    assert all([card.is_trump for card in choices])
    if not has_opponent_left:
      for card in choices:
        # last player: play (first) high score card if available
        if card.is_high_score_low_value_card:
          return card
    return FixedBetterRulesPlayer._select_useless_card(choices, game_type)

  @staticmethod
  def _select_high_scoring_or_useless_card(choices, has_opponent_left, game_type):
    """
    Selects a high-scoring non-trump card if possible or a "useless" card otherwise.

    :choices: List of cards that could be selected.
    :game_type: Type of the game.

    :returns: Selected card.
    """
    if game_type.is_trump_game_type and has_opponent_left:
      # don't play a high-scoring card during a trump game if there are still opponents
      return FixedBetterRulesPlayer._select_useless_card(choices, game_type)

    # get high-scoring cards; sort them by score descending
    all_trumps = all(map(lambda card: card.is_trump, choices))
    high_scoring = list(sorted(filter(
      lambda card: card.is_high_score_low_value_card and (not card.is_trump or all_trumps), choices),
      key=lambda card: card.score, reverse=True))

    # we have no high-scoring cards, return useless card
    if not high_scoring:
      return FixedBetterRulesPlayer._select_useless_card(choices, game_type)

    # we do have high-scoring cards, return the card with max score with number of cards per suit as tiebreaker
    suit_counts = FixedBetterRulesPlayer._get_counts_per_suit(choices)
    card_to_play = high_scoring[0]
    for card in high_scoring:
      if card.score >= card_to_play.score and suit_counts[card.suit] < suit_counts[card_to_play.suit]:
        card_to_play = card
    assert not (all_trumps ^ card_to_play.is_trump), "only select a trump if really needed"
    return card_to_play

  @staticmethod
  def _select_useless_card(choices, game_type):
    """
    Selects a "useless" card.
    Note that counterintuitively, it's better to select the card among all cards, rather than only
    among the low-scoring cards.

    :choices: List of cards that could be selected.
    :game_type: Type of the game.

    :returns: Selected card.
    """
    # separating the low-scoring cards doesn't seem to help...
    suit_counts = FixedBetterRulesPlayer._get_counts_per_suit(choices)
    all_trumps = all(map(lambda card: card.is_trump, choices))
    card_to_play = choices[0]
    for card in choices:
      # don't select a trump if not necessary
      if not all_trumps:
        if not card_to_play.is_trump and card.is_trump:
          # don't select a trump when the current one isn't
          continue
        if card_to_play.is_trump and not card.is_trump:
          # select any card other than a trump when the current one is
          card_to_play = card
          continue
      suit_count_diff = suit_counts[card.suit] - suit_counts[card_to_play.suit]
      value_diff = (card.value - card_to_play.value) * (-1 if game_type == GameType.UNNENUFE else 1)
      if card.is_nell:
        value_diff += 6
      if card_to_play.is_nell:
        value_diff -= 6
      if card.is_buur:
        value_diff += 5
      if card_to_play.is_buur:
        value_diff -= 5
      score_diff = card.score - card_to_play.score

      # this weighting seems to be work best...
      if (1*value_diff) + (1*score_diff) + (3*suit_count_diff) < 0:
        card_to_play = card
    assert not (all_trumps ^ card_to_play.is_trump), "only select a trump if really needed"
    return card_to_play

  @staticmethod
  def _select_card_player_1(valid_cards, game_type, log):
    # first player: choose best card
    for card in valid_cards:
      # pull trumps if available
      if game_type.is_trump_game_type and card.is_trump and card.value <= Card.VALUE_ACHT:
        log.debug("First player tries to pull trumps with a low trump: {}".format(card))
        return card

    log.debug("First player chooses the best card")
    return RulesPlayer._select_best_card_of_first_non_trump_suit(valid_cards)

  @staticmethod
  def _select_card_player_2(valid_cards, played_cards, game_type, log):
    # second player: check if he can beat the first player
    beating_cards = list(filter(played_cards[0].is_beaten_by, valid_cards))
    worst_valid_card = FixedBetterRulesPlayer._select_useless_card(valid_cards, game_type)
    if not beating_cards:
      # first player can't be beat: play worst card
      log.debug("Second player can't beat first one, selecting worst valid: {}".format(worst_valid_card))
      return worst_valid_card

    worst_beating_card = FixedBetterRulesPlayer._select_useless_card(beating_cards, game_type)
    if not worst_beating_card.is_trump or played_cards[0].is_trump:
      # the worst beating isn't a trump or it's a trump round - beat the first player "normally"
      log.debug("Second player can beat first one, selecting worst beating: {}".format(worst_beating_card))
      return worst_beating_card

    assert all(map(lambda card: card.is_trump, beating_cards)), \
        "since the worst beating is a trump, all must be trumps"

    # decide whether to play a trump (stechen)
    points = sum(map(lambda card: card.score, played_cards))
    if points >= FixedBetterRulesPlayer.STECHEN_THRESHOLD_EARLY:
      trump_card = FixedBetterRulesPlayer._select_trump_card(beating_cards, True, game_type)
      log.debug("Second player stichs with worst trump: {}".format(trump_card))
      return trump_card

    log.debug("Second player can't beat with same suit but doesn't stich, selecting worst card: {}"
        .format(worst_valid_card))
    return worst_valid_card

  @staticmethod
  def _select_card_player_3(valid_cards, played_cards, game_type, log):
    # third player: check if the round currently belongs to the team
    if not played_cards[0].is_beaten_by(played_cards[1]):
      # the round is the first player's: play the highest-score or worst card
      worst_card = FixedBetterRulesPlayer._select_high_scoring_or_useless_card(valid_cards, True, game_type)
      log.debug("Third player plays card with high score or worst because round belongs to team: {}"
          .format(worst_card))
      return worst_card

    # the round isn't the first player's: check if he can beat player 2
    beating_cards = list(filter(played_cards[1].is_beaten_by, valid_cards))
    worst_valid_card = FixedBetterRulesPlayer._select_useless_card(valid_cards, game_type)
    if not beating_cards:
      # second player can't be beat: play worst card
      log.debug("Third player can't beat second one, selecting worst valid: {}".format(worst_valid_card))
      return worst_valid_card

    worst_beating_card = FixedBetterRulesPlayer._select_useless_card(beating_cards, game_type)
    if not worst_beating_card.is_trump or played_cards[0].is_trump:
      # the worst beating isn't a trump or it's a trump round - beat the second player "normally"
      log.debug("Third player can beat second one, selecting worst beating: {}".format(worst_beating_card))
      return worst_beating_card

    assert all(map(lambda card: card.is_trump, beating_cards)), \
        "since the worst beating is a trump, all must be trumps"

    # decide whether to play a trump (stechen)
    points = sum(map(lambda card: card.score, played_cards))
    if points >= FixedBetterRulesPlayer.STECHEN_THRESHOLD_EARLY:
      trump_card = FixedBetterRulesPlayer._select_trump_card(beating_cards, True, game_type)
      log.debug("Third player stichs with worst trump: {}".format(trump_card))
      return trump_card

    log.debug("Third player can't beat with same suit but doesn't stich, selecting worst card: {}"
        .format(worst_valid_card))
    return worst_valid_card

  @staticmethod
  def _select_card_player_4(valid_cards, played_cards, game_type, log):
    # fourth player: check if the round currently belongs to the team
    if played_cards[0].is_beaten_by(played_cards[1]) and not played_cards[1].is_beaten_by(played_cards[2]):
      # the round is the second player's: play the highest-score or worst card
      worst_card = FixedBetterRulesPlayer._select_high_scoring_or_useless_card(valid_cards, False, game_type)
      log.debug("Fourth player plays card with high score or worst because round belongs to team: {}"
          .format(worst_card))
      return worst_card

    # the round isn't the second player's: check if the round can be won
    beating_cards = list(filter(lambda my_card:
      played_cards[0].is_beaten_by(my_card) and played_cards[2].is_beaten_by(my_card), valid_cards))
    worst_valid_card = FixedBetterRulesPlayer._select_useless_card(valid_cards, game_type)
    if not beating_cards:
      # the round can't be won: play worst card
      log.debug("Fourth player can't win round, selecting worst card: {}".format(worst_valid_card))
      return worst_valid_card

    high_scoring_or_worst_beating = FixedBetterRulesPlayer._select_high_scoring_or_useless_card(
        beating_cards, False, game_type)
    if not high_scoring_or_worst_beating.is_trump or played_cards[0].is_trump:
      # the worst beating isn't a trump or it's a trump round - beat the second player "normally"
      log.debug("Fourth player can win the round, selecting high-scoring or worst beating: {}"
          .format(high_scoring_or_worst_beating))
      return high_scoring_or_worst_beating

    assert all(map(lambda card: card.is_trump, beating_cards)), \
        "since the worst beating is a trump, all must be trumps"

    # decide whether to play a trump (stechen)
    points = sum(map(lambda card: card.score, played_cards))
    if points >= FixedBetterRulesPlayer.STECHEN_THRESHOLD_LATE:
      trump_card = FixedBetterRulesPlayer._select_trump_card(beating_cards, False, game_type)
      log.debug("Fourth player stichs with high-scoring or worst trump: {}".format(trump_card))
      return trump_card

    log.debug("Fourth player can't beat with same suit but doesn't stich, selecting worst card: {}"
        .format(worst_valid_card))
    return worst_valid_card

  def _select_card(self, args, log):
    valid_cards, played_cards, _, game_type = args

    if len(valid_cards) == 1:
      log.debug("Player plays only valid card: {}".format(valid_cards[0]))
      return valid_cards[0]

    if len(played_cards) == 0: # pylint: disable=len-as-condition
      return FixedBetterRulesPlayer._select_card_player_1(valid_cards, game_type, log)

    if len(played_cards) == 1:
      return FixedBetterRulesPlayer._select_card_player_2(valid_cards, played_cards, game_type, log)

    if len(played_cards) == 2:
      return FixedBetterRulesPlayer._select_card_player_3(valid_cards, played_cards, game_type, log)

    return FixedBetterRulesPlayer._select_card_player_4(valid_cards, played_cards, game_type, log)

  def _select_game_type(self):
    raise NotImplementedError()
