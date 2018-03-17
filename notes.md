# Setup for comparisons
- Play at least 5e5 hands - 1e5 seems a bit few whereas 1e6 takes disproportionately much time.
  5e5 should be about 60 min per prediction model
- No need to specify seed

# Setup for training
- Use seed for reproducibility

# Discoveries
- Encodings 1-4 are retired (useless attempts)
- SGD doesn't work
- Training doesn't work as well when playing the best card
- Training interval has an impact on learning performance - really, or is this
  due to the comparison of bad models?
- 1 hidden layer is insufficient, 2 also doesn't seem to be optimal
- Training time: maybe 1 -> x layers = +4h; +100 neurons -> +4h
- Small layers are useless (when all layers are the same width)

# To try
- Cost? Encoding? Model parameters? Models?
- How much data is needed/useful for MLP?
- Do initial training on data from model vs simple
- Encodings 3, 4 -> ?
- "relative" player encoding -> does that reduce data need 4-fold?
- "uneven" layer architectures

