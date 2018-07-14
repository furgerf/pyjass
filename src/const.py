#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Const:
  """
  Number of cards per player; this corresponds to the number of cards per suit.
  """
  CARDS_PER_PLAYER = 9

  """
  Number of players; this corresponds to the number of players.
  """
  PLAYER_COUNT = 4

  """
  Number of cards that are played during one hand.
  """
  CARDS_PER_HAND = CARDS_PER_PLAYER * PLAYER_COUNT

  """
  Number of decisions that are made during one hand - playing the last card doesn't require a decision.
  """
  DECISIONS_PER_HAND = (CARDS_PER_PLAYER - 1) * PLAYER_COUNT

  """
  Target score of a single game.
  """
  WINNING_SCORE = 1000

  """
  Number of bytes required to store one sample - number of cards * 1 byte + 2 bytes for the score.
  """
  BYTES_PER_SAMPLE = CARDS_PER_HAND + 2

  """
  Size of a chunk of offline data to process.
  """
  OFFLINE_CHUNK_SIZE = int(3.2e6)

  """
  All card codes must be in this range to be valid.
  """
  MIN_CARD_CODE = 0
  MAX_CARD_CODE = 255
