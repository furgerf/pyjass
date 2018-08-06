#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum, unique


@unique
class GameType(Enum):
  OBENABE = 0
  UNNENUFE = 1
  TRUMP_SPADES = 2
  TRUMP_HEARTS = 3
  TRUMP_DIAMONDS = 4
  TRUMP_CLUBS = 5

  @property
  def is_trump_game_type(self):
    return self == GameType.TRUMP_SPADES or self == GameType.TRUMP_HEARTS or \
        self == GameType.TRUMP_DIAMONDS or self == GameType.TRUMP_CLUBS
