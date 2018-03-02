# Setup for comparisons
- Play at least 5e5 hands - 1e5 seems a bit few whereas 1e6 takes disproportionately much time.
  5e5 should be about 60 min per prediction model
- No need to specify seed

# Setup for training
- Use seed for reproducibility

# Discoveries
- Encoding 2 doesn't work
- SGD doesn't work
- Training with with playing the best card seems to be better
  - This seems to be true for training on bad data but probably not for better data!
- So far, encodings 3 and 4 seem to perform similarly

# To try
- How do methods compare against better baseline?
- Is training more effective against better-than-random player?
  -> Would make sense, since we're interested in the good decisions
- Cost? Encoding? Model parameters? Models?
- How much data is needed/useful for MLP?
- Encodings 3, 4 -> ?

