# Setup for comparisons
- Play at least 5e5 hands - 1e5 seems a bit few whereas 1e6 takes disproportionately much time
- No need to specify seed

# Setup for training
- Use seed for reproducibility

# Discoveries
- SGD doesn't work
- 1 hidden layer is insufficient, 2 also doesn't seem to be optimal
- Small layers are useless
- Model 19: 3x100 and 5x100 are significantly worse than 4x100 (~5%)
  - 3x100 probably because it's underfitting
  - 5x100 possibly because it's training offline or because it's training on "foreign" data
- Comparing baselines: the differences are small, but:
  - The models seem to be slightly better against "their" baseline
  - In direct comparison, 3x100 is about the same, 4x100 against simple and 5x100 against better are better
- Highlighting team-mate with a relative player encoding clearly works better than absolute encoding
  or not highlighting team-mate
- Weighting score of hand seems better than score of round; so far tried 1:2, 2:1, 4:1 without finding
  an upper limit (*should be explored further*)
- Training on "own data" only doesn't seem to help
- Fewer but wider layers seems better (e.g. 4x200 instead of 6x100), though there shouldn't be too
  few layers (probably, that's why 300-200-300 doesn't work) - *should be explored further*
- Looks like many "normal" layers, e.g. 10x100 doesn't work well
- unnenufe seems to be slightly easier than obenabe (ie, the baseline is a bit worse) but the models work roughly the same

# To try
- Cost? Encoding? Model parameters? Models?
- "uneven" layer architectures
- Tensorflow, Keras, RNN

