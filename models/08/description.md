# Iteration 8
32m data point
cost: 2\*score of round + score of hand
_same as 6 but training vs simple and small offline_

## Results
### Round 1: Trained on 32m offline and 288m online samples (mlp vs simple)
mlp vs sim: 14% trained playing the best card
mlp vs sim: 22% trained NOT playing the best card

*Conclusions*:
- training on 320m "good" samples beats training on 640 "bad" samples
- with good data, it seems training is more effective when not playing the best card

