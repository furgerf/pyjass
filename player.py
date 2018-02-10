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


class Player():
  training_data = None

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
      pickle_file_name = "model.pkl"
      if path.exists(pickle_file_name):
        with open(pickle_file_name, "rb") as fh:
          self.log.warning("Loading model from {}...".format(pickle_file_name))
          self._regressor = pickle.load(fh)
      else:
        if Player.training_data is None:
          file_name = "bar.csv"
          self.log.warning("Loading data from {}...".format(file_name))
          Player.training_data = np.genfromtxt(file_name, delimiter=",", dtype=int, skip_header=1)
        self._regressor = RandomForestRegressor()
        self.log.warning("Fitting regressor...")
        self._regressor.fit(Player.training_data[:,:-1], Player.training_data[:,-1])
        with open(pickle_file_name, "wb") as fh:
          pickle.dump(self._regressor, fh)

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

    scores = self._regressor.predict(states)
    self.log.debug("Playing cards {} has predicted score of {}".format(utils.format_cards(valid_cards), scores))
    return valid_cards[np.argmax(scores)]

