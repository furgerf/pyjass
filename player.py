#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import pandas as pd
import csv
import pickle
from os import path

import numpy as np

import utils
from card import Card
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import SGDRegressor


class Player():
  regressor = None

  def __init__(self, name, selection, log):
    self._name = name
    self._selection = selection
    self._left = None
    self._team = None
    self._right = None
    self._hand = None
    self.log = log
    self.card_selections = {
        "random": self._randomly_select_card,
        "highest": self._select_highest_card,
        "rf": self._select_with_rf,
        }
    if self._selection == "rf":
      pickle_file_name = "new-model.pkl"
      if Player.regressor is not None:
        return

      if path.exists(pickle_file_name):
        with open(pickle_file_name, "rb") as fh:
          self.log.warning("Loading model from {}...".format(pickle_file_name))
          Player.regressor = pickle.load(fh)
      else:
        file_name = "bar.csv"
        Player.regressor = MLPRegressor(warm_start=True)
        offset = 0
        chunk_size = int(1e6)
        while True:
          self.log.warning("Loading data from {}...".format(file_name))
          training_data = np.genfromtxt(file_name, delimiter=",", dtype=int, skip_header=1+offset, max_rows=chunk_size)
          if not len(training_data):
            break
          offset += chunk_size
          self.log.warning("Fitting regressor with {} examples...".format(len(training_data)))
          Player.regressor.partial_fit(training_data[:,:-1], training_data[:,-1])
        self.log.warning("Writing model to {}...".format(pickle_file_name))
        with open(pickle_file_name, "wb") as fh:
          pickle.dump(Player.regressor, fh)

  def set_players(self, left, team, right):
    self._left = left
    self._team = team
    self._right = right

  @property
  def name(self):
    return self._name

  @property
  def hand(self):
    return self._hand

  @hand.setter
  def hand(self, hand):
    self._hand = sorted(hand, key=lambda c: str(c.suit) + str(c.value))

  def select_card_to_play(self, played_cards, known_cards):
    if played_cards:
      # try to match suit
      valid_cards = list(filter(lambda c: played_cards[0].suit == c.suit, self.hand))
      if not valid_cards:
        # can't match suit, any card is allowed
        valid_cards = self.hand
    else:
      valid_cards = self.hand

    selected_card = self.card_selections[self._selection]((valid_cards, played_cards, known_cards))
    self.log.debug("{} selects card {} to play (valid: {})".format(self.name, selected_card, utils.format_cards(valid_cards)))

    encoded_player_state = self._encode_cards(played_cards, known_cards)
    encoded_player_state[selected_card.card_index] = Card.SELECTED

    return selected_card, encoded_player_state

  def _encode_cards(self, played_cards, known_cards):
    cards = np.array(known_cards, copy=True)
    for pc in played_cards:
      if cards[pc.card_index] != 0:
        raise ValueError()
      cards[pc.card_index] = Card.IN_PLAY
    for hc in self.hand:
      if cards[hc.card_index] != 0:
        raise ValueError()
      cards[hc.card_index] = Card.IN_HAND
    return cards

  def _randomly_select_card(self, args):
    valid_cards = args[0]
    return valid_cards[np.random.randint(len(valid_cards))]

  def _select_highest_card(self, args):
    valid_cards = args[0]
    return valid_cards[-1]

  def _select_with_rf(self, args):
    valid_cards, played_cards, known_cards = args
    state = self._encode_cards(played_cards, known_cards)
    states = []
    scores = []
    for i in range(len(valid_cards)):
      card = valid_cards[i]
      my_state = np.array(state, copy=True)
      my_state[card.card_index] = Card.SELECTED
      states.append(my_state)

    scores = Player.regressor.predict(states)
    # TODO: Select according to probability relative to score
    card = valid_cards[np.argmax(scores)]
    self.log.debug("Playing cards {} has predicted score of {}, selecting {}".format(utils.format_cards(valid_cards), scores, card))
    return card

