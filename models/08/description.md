# Iteration 8
32m data point
cost: score of round + score of hand
_same as 6 but training vs simple and small offline_

## Results
### Round 1: Trained on 32m offline and 288m online samples (mlp vs simple)
mlp vs sim: 14% trained playing the best card
mlp vs sim: 22% trained NOT playing the best card

*Conclusions*:
- training on 320m "good" samples beats training on 640m "bad" samples
- with good data, it seems training is more effective when not playing the best card

### Round 2: Based on round 1 plus 320m vs simple
mlp vs sim: 17% trained playing the best card both times
mlp vs sim: x% trained NOT playing the best card both times

*Conclusions*:
- 

### Independent: Based on round 1 (NOT best) + 320m samples online
mlp vs sim: x% trained mlp vs mlp (both NOT best)
mlp vs sim: x% trained mlp vs sim (mlp NOT best)

