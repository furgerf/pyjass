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
- Training interval has an impact on learning performance - sometimes(?)
- Changing model parameters on a trained model doesn't seem to work (no change
  when modifying learning\_rate\_init and max\_iter) but change when when
  modifying batch\_size!)

# To try
- Cost? Encoding? Model parameters? Models?
- How much data is needed/useful for MLP?
- Encodings 3, 4 -> ?

