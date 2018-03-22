#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Encoding:

  # pylint: disable=too-many-arguments
  def __init__(self, card_code_players, card_code_in_hand, card_code_in_play, card_code_selected,
      round_score_factor, hand_score_factor):
    self._card_code_players = card_code_players
    self._card_code_in_hand = card_code_in_hand
    self._card_code_in_play = card_code_in_play
    self._card_code_selected = card_code_selected
    self._round_score_factor = round_score_factor
    self._hand_score_factor = hand_score_factor


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


  def __str__(self):
    return str(self.__dict__)
