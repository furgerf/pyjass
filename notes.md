# Setup for comparisons
- Play at least 5e5 hands - 1e5 seems a bit few whereas 1e6 takes disproportionately much time.
  5e5 should be about 60 min per prediction model
- No need to specify seed

# Setup for training
- Use seed for reproducibility

# Discoveries
- Encoding 2 doesn't seem to work well
- SGD doesn't work
- Training with with playing the best card seems to be better

# To try
- How do methods compare against better baseline?
- Is training more effective against better-than-random player?
  -> Would make sense, since we're interested in the good decisions
- Cost? Encoding?
- Encodings 3, 4 -> ?

