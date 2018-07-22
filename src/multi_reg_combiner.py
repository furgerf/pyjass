#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
from argparse import ArgumentParser


def load_regressor(model, name):
  file_name = "models/{}/{}".format(model, name)
  with open(file_name, "rb") as fh:
    return pickle.load(fh)

def main():
  parser = ArgumentParser()
  parser.add_argument("--model", required=True,
      help="Name of the folder in the models/ directory")
  parser.add_argument("--multi-regressor-name", required=True,
      help="Name of the combined multi-regressor")
  parser.add_argument("--regressors", required=True,
      help="Comma-separated list of regressor names to combine")
  args = parser.parse_args()

  regressors = [load_regressor(args.model, name) for name in args.regressors.split(",")]
  game_types = [regressor.game_type for regressor in regressors]
  assert len(game_types) == len(set(game_types)), "Only need one regressor per game type"

  combined_regressors = {regressor.game_type: regressor for regressor in regressors}
  file_name = "models/{}/{}".format(args.model, args.multi_regressor_name)
  with open(file_name, "wb") as fh:
    pickle.dump(combined_regressors, fh)
  print("Combined {} regressors ({}) to single multi-regressor '{}' ({})".format(
    len(regressors), args.regressors, args.multi_regressor_name, file_name))

if __name__ == "__main__":
  main()
