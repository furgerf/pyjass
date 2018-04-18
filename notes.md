# Setup for comparisons
- Play at least 5e5 hands - 1e5 seems a bit few whereas 1e6 takes disproportionately much time.
  5e5 should be about 60 min per prediction model
- No need to specify seed

# Setup for training
- Use seed for reproducibility

# Discoveries
- SGD doesn't work
- 1 hidden layer is insufficient, 2 also doesn't seem to be optimal
- Small layers are useless (when all layers are the same width)
- Model 19: 3x100 and 5x100 are significantly worse than 4x100 (~5%)
  - 3x100 probably because it's underfitting
  - 5x100 possibly because it's training offline or because it's training on "foreign" data
- Comparing baselines: the differences are small, but:
  - The models seem to be slightly better against "their" baseline
  - In direct comparison, 3x100 is about the same, 4x100 against simple is better, 5x100 against better is better
- Training against better baseline (model 20) has roughly the same results as model 20, but about 10% lower win%

# To try
- Cost? Encoding? Model parameters? Models?
- "uneven" layer architectures

