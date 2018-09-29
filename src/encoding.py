#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

from const import Const


class Encoding:

  # pylint: disable=too-many-arguments
  def __init__(self, baseline, card_code_players, card_code_in_hand, card_code_in_play, card_code_selected,
      round_score_factor, hand_score_factor,
      relative_player_encoding=False, relative_in_play_encoding=False,
      card_index_by_suit=False, sort_states=False, trump_code_offset=0):

    all_non_trump_codes = np.array(card_code_players + [card_code_in_hand] + [card_code_selected] + \
        (card_code_in_play if isinstance(card_code_in_play, list) else [card_code_in_play]))
    if trump_code_offset == 0:
      all_codes = all_non_trump_codes
    else:
      all_trump_codes = all_non_trump_codes + trump_code_offset
      all_codes = list(all_trump_codes) + list(all_non_trump_codes)

    # ensure that no code is out of bounds
    assert min(all_codes) >= Const.MIN_CARD_CODE and max(all_codes) <= Const.MAX_CARD_CODE
    # ensure that no code is assigned multiple times
    assert len(set(all_codes)) == len(all_codes)

    # ensure that we get a list or an int
    assert relative_in_play_encoding == isinstance(card_code_in_play, list)
    assert relative_in_play_encoding != isinstance(card_code_in_play, int)

    self._baseline = baseline
    self._card_code_players = card_code_players
    self._card_code_in_hand = card_code_in_hand
    self._card_code_in_play = card_code_in_play
    self._card_code_selected = card_code_selected
    self._round_score_factor = round_score_factor
    self._hand_score_factor = hand_score_factor
    self._relative_player_encoding = relative_player_encoding
    self._relative_in_play_encoding = relative_in_play_encoding
    self._card_index_by_suit = card_index_by_suit
    self._sort_states = sort_states
    self._trump_code_offset = trump_code_offset


  @property
  def baseline(self):
    return self._baseline


  @property
  def card_code_players(self):
    return self._card_code_players

  @property
  def card_code_in_hand(self):
    return self._card_code_in_hand

  @property
  def card_code_in_play(self):
    return self._card_code_in_play

  @property
  def card_code_selected(self):
    return self._card_code_selected

  @property
  def trump_code_offset(self):
    return self._trump_code_offset


  @property
  def round_score_factor(self):
    return self._round_score_factor

  @property
  def hand_score_factor(self):
    return self._hand_score_factor


  @property
  def relative_player_encoding(self):
    # a relative player encoding means that the first entry in card_code_players corresponds to the
    # next player (right of the current player), second entry is the team member, etc.
    return self._relative_player_encoding

  @property
  def relative_in_play_encoding(self):
    # a relative in-play encoding means that the first entry in card_code_in_play corresponds to the
    # previous player (left of the current player), second entry is the team member, etc.
    return self._relative_in_play_encoding

  @property
  def card_index_by_suit(self):
    # the card index should group the cards by suit (keeping cards of the same suit together) instead
    # of grouping by value
    return self._card_index_by_suit

  @property
  def sort_states(self):
    # sorting the states means that the order of the suits can be determined so that every
    # unique state represents 6 actual states (with different ordering of the suits)
    return self._sort_states


  @property
  def training_data_header(self):
    header = "36 rows for cards with their known state from the view of a player " + \
        "(0 unknown, {} played by {} player, {} in play, {} in hand, {} selected to play; " + \
        "score of round from the view of the player: round factor {}, hand factor {}, baseline {}\n"
    return header.format(self.card_code_players, "relative" if self.relative_player_encoding else "absolute",
        self.card_code_in_play, self.card_code_in_hand, self.card_code_selected,
        self.round_score_factor, self.hand_score_factor, self.baseline)

  def __str__(self):
    return str(self.__dict__)
