#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

import utils


class Round():

  def __init__(self, players, known_cards, log):
    self._players = players
    self._known_cards = known_cards
    self.p1, self.p2, self.p3, self.p4 = players
    self.log = log

  def play(self, dealer):
    # self._print_hands()

    played_cards = []
    states = []
    for i in range(4):
      current_player = self._players[(dealer+i) % 4]
      played_card, player_state = current_player.select_card_to_play(played_cards, self._known_cards)
      current_player.hand.remove(played_card)

      played_cards.append(played_card)
      states.append(player_state)

    winner, score = self._evaluate(played_cards, dealer)
    self.log.info("{} wins the round ({} points)".format(self._players[winner].name, score))
    return winner, np.roll(played_cards, -dealer), score, np.roll(states, -dealer)

  def _evaluate(self, played_cards, dealer):
    best_index = 0
    for i in range(1, 4):
      if played_cards[best_index].is_beaten_by(played_cards[i]):
        best_index = i
    winner = (dealer + best_index) % 4

    score = sum(map(lambda c: c.score, played_cards))

    return winner, score

  def _print_hands(self):
    print("\t{}: {}".format(self.p3.name, utils.format_cards(self.p3.hand)))

    print("{}:\t\t\t\t\t{}:".format(self.p4.name, self.p2.name))
    for i in range(9):
      if i >= len(self.p2.hand):
        print("")
        continue
      print("{}\t\t\t\t\t{}".format(self.p4.hand[i], self.p2.hand[i]))

    print("\t{}: {}".format(self.p1.name, utils.format_cards(self.p1.hand)))

