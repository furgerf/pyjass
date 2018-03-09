# Iteration 11
32m data point
cost: 4\*score of round + score of hand
_finally trying different cost; training vs simple and small offline_

NOTE: It's possible there was still some issue with encoding during the training/testing but I don't think so.

## Results
### Round 1: Trained on 32m offline and 288m online samples (mlp vs simple)
mlp vs sim: 11% trained playing probability card <-- this model crashed during training and the last 10% had to be re-trained

*Conclusions*:
- the initial result with this cost is significantly worse than the previous standard cost
- maybe training with this modified implementation really doesn't work?

### Round 2: Based on round 1 + 320m vs simple
mlp vs sim: 10% trained playing probability card

*Conclusions*:
- maybe training with this modified implementation really doesn't work?

