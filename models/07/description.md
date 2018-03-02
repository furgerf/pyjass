# Iteration 7
320m data point
cost: score of round + score of hand
_modified card encoding and reduced score of round_

## Results
### Round 1: Trained on 320m offline samples (rnd vs rnd)
sgd vs rnd: 52%/57% (probability/best)
mlp vs rnd: 56%/87%
sgd vs mlp: 14%/9%

### Round 2: Trained on 320m offline samples (rnd vs rnd) + 320m online samples (mlp vs rnd)
Trained by playing based on probabilities _I think_:
mlp vs sim: 8%
Trained by playing best card:
mlp vs sim: 11%

*Conclusions*:
- when training on data from rnd, playing the best card trains better

### Round 3: Trained with 32m offline samples (rnd vs rnd) + 288m online samples
Online samples vs rnd:
mlp vs sim: 2%
Online samples vs mlp:
mlp vs sim: 23%

*Conclusions*:
- training on data from mlp is much better than data from rnd (duh)

