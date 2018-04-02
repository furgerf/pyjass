#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Encoding:

  # pylint: disable=too-many-arguments
  def __init__(self, card_code_players, card_code_in_hand, card_code_in_play, card_code_selected,
      round_score_factor, hand_score_factor, relative_player_encoding):
    if set([0, card_code_in_hand, card_code_in_play, card_code_selected]).intersection(card_code_players):
      raise ValueError("Can't use same number for multiple states")

    self._card_code_players = card_code_players
    self._card_code_in_hand = card_code_in_hand
    self._card_code_in_play = card_code_in_play
    self._card_code_selected = card_code_selected
    self._round_score_factor = round_score_factor
    self._hand_score_factor = hand_score_factor
    self._relative_player_encoding = relative_player_encoding


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
  def round_score_factor(self):
    return self._round_score_factor

  @property
  def hand_score_factor(self):
    return self._hand_score_factor


  @property
  def relative_player_encoding(self):
    return self._relative_player_encoding


  @property
  def training_data_header(self):
    header = "36 rows for cards with their known state from the view of a player " + \
        "(0 unknown, {} played by {} player, {} in play, {} in hand, {} selected to play; " + \
        "score of round from the view of the player: round factor {}, hand factor {}\n"
    return header.format(self.card_code_players, "relative" if self.relative_player_encoding else "absolute",
        self.card_code_in_play, self.card_code_in_hand, self.card_code_selected,
        self.round_score_factor, self.hand_score_factor)

  def __str__(self):
    return str(self.__dict__)
