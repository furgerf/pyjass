# Overview
The purpose of this project is to develop a machine-learning-based bot which
plays the Swiss game of "Jass". Consequently, there doesn't currently exist a
facility for human players to play against the trained bots.

The infrastructure is geared towards training ML-models by playing large amounts
of games against opponents which are based on a few rules and serve as a
baseline. These games include decisions which are encoded as decision states and
are rewarded, based on the result of the game. Thus, this approach is based on
reinforcement learning.

# Installation
The application requires python 3.5 or later and relies on `virtualenv` to be
available. Currently, only Linux-based systems are supported. In order to run
the application, install the dependencies in a virtual environment by running
`make install`.

# Infrastructure
The application entry point is `src/run.py`, which sets up and runs the game,
according to the supplied arguments. To facilitate the usage of the arguments,
different (phony) targets are defined in `makefile`.

Each evaluation has an evaluation ID which is assigned based on a GUID if not
specified. The evaluation log, as well as results, scores, and models are stored
in the respective directory `evaluations/<evaluation-id>`.

Typically, large amounts of _hands_ are played in parallel, where several
parameters are used to specify intervals for logging, checkpoints, training,
etc. There are several dependencies among these parameters, which are mentioned
if violated.

Training data can be stored or loaded, which is also specified with command line
arguments. Only the desired file names should be specified, the data is then
automatically placed in or retrieved from the `data/`-directory.

The regressors to load and store should also only be specified as file names.
The actual paths is then of the form `models/<model-number>/<regressor-name>`.

## Evaluation types
Three different types of evaluations can be used, which are described in the
following.

### Evaluation
To test the performance of a model, run `make eval` with the desired arguments.
By default, 500k hands are played to obtain a reasonable indication of the
expected performance of the two types of players (by default, a ML player
against a baseline). These hands are distributed across 2 cores by default.

### Training
A _regressor_ is trained by running `make train`.  Training is organized into
_rounds_, where a round consists of 4M hands by default, which are also
typically distributed across 2 cores. Optionally, the regressor can also be
trained from previously-stored data (_offline_ training) before the actual hands
are played (_online_ training). The data from these online hands may also be
stored, for training of other regressors.

To reduce errors when scheduling training, additional convenience targets are
defined in the makefile.

Note that regressor training typically tries to utilize all available cores, so
that the effective usage is beyond the specified number of processes. This
specified number of processes only affects the playing of games (data
generation).

### Initial data generation
When new regressors or state encodings are introduced, the initial training is
done on data from games among baseline methods. To generate this initial data,
run `make store`, which stores the data from 4M hands that are run on 4 parallel
processes by default.

# Code architecture
The following section gives a brief overview over the source code.

Note that, since this project's primary focus is to train and evaluate models,
there's no distinction into traditional "games" which end once one team reaches
the required amount of points. Instead, the unit which is used to determine the
"amount of playing" is the "hand" (see below).

The `Game` constructs the harness which makes sure that the requested amount of
`Hand`s are played, with the desired aspects such as online training or storage
of training data.

The hands are then actually played in a `ParallelGame`. Initially, one
`ParallelGame` is created per core that should be used. A _batch_ of hands is
then played concurrently by each parallel game. Note that a limiting factor for
the batch size is the available memory in case training data should be stored.
Furthermore, the batch size and number of processes needs to match the desired
intervals.

An individual `Hand` refers to shuffling, distributing, and subsequently playing
the 36 cards. A hand consists of 9 `Round`s; each round consists of each of the
4 players playing a card.

A `Player` is a participant in the game which makes decisions such as selecting
the game type or selecting the card to play. Specific types of players are
created using inheritance, which distinguishes `BaselinePlayer`s such as
`RadomCardPlayer`, `HighestCardPlayer`, or `RulesPlayer`s such as
`SimpleRulesPlayer` or `BetterRulesPlayer`, and finally `LearnerPlayer`s. There
are currently only `SgdPlayer` (which turned out to be useless) and `MlpPlayer`,
which are based on stochastic gradient descent and multi-layer perceptrons,
respectively. Both of these models are only learning a specific game type and
are designed to be combined by a `MultiRegPlayer` that uses one regressor per
game type. Note that this isn't currently implemented yet.

Note that the type of player/bot is selected per team, so that two players of
one type play against two players of another (or same) type.

An important aspect is the `Encoding`, which specifies how a decision state
should be encoded and how to determine the reward of a specific decision.

The decision state for selecting a card to play is a 36-component vector, where
each component stands for a card, with the value (one byte: 0- 255) representing
the card's known location from the view of the decision-making player according
to the encoding.

Beside selecting the value of a card that e.g. is currently in play, the
encoding also encompasses further aspects of the encoding, such as using
relative player numbers (instead of absolute) or re-arranging the suits (when
they're equivalent) to reduce the manifold to learn.

Note that the terminology and distinction unfortunately isn't very clear. A
"model" or "model number" is linked to a specific "encoding". However, different
"models" can use the same "encoding".

The decision state for game type selection (and thus training of this decision)
isn't yet implemented.

# Findings
- Plain MLPs work fairly well as soon as multiple layers are used. The default
  layer width of 100 is ok, but wider layers (e.g. 200) work better.
- Fiddling with model parameters beside the layers, such as learning rate,
  didn't yield noticeably different results.
- Baselines such as random are far too weak to compete with MLP models. With
  improvements in the encoding, a third iteration of the rule-based baseline
  becomes necessary.
- Somewhat counter-intuitively, basing the reward (cost) more on the overall
  score of the hand, rather than the specific round produces superior results.
  It remains to be seen if only using the score of the hand is even better.

# Missing game aspects
The following aspects of the game aren't currently implemented:

- Trump-based game types
- "Schieben"
- Winning all rounds "Match" should yield 100 points additionally

