# Iteration 6
320m data point
cost: score of round + score of hand
_modified card encoding_

## Results
### Round 1: Trained on 320m offline samples (rnd vs rnd)
sgd vs rnd: 52%/56% (probability/best)
mlp vs rnd: 60%/84%
sgd vs mlp: 42%/15%

### Round 2: Trained on 320m offline samples (rnd vs rnd) + 320m online samples (mlp vs rnd)
#### Round 2.1: Trained by playing card based on probability
sgd vs rnd: 50%/52%
mlp vs rnd: 57%/91%
sgd vs mlp: 43%/4%

#### Round 2.2: Trained by playing best card
sgd vs rnd: 51%/59%
mlp vs rnd: 61%/95%
sgd vs mlp: 39%/3%
mlp vs sim: /16%

*Conclusions*:
- sgd doesn't work
- mlp with 640m samples is better than with 320m
- training vs random is better with best card selection -> probably because rnd makes bad choices
- not playing the best card is useless for model evaluation

### Round 3: Trained on 320m offline samples (rnd vs rnd) + 320m online samples (mlp vs rnd) + 64m online samples (mlp vs mlp)
mlp vs rnd: 59%/97%
mlp vs sim: /31%

*Conclusions*:
- mlp benefits from more data, especially from samples of "good" choices

