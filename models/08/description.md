# Iteration 8
32m data point
cost: score of round + score of hand
_same as 6 but training vs simple and small offline_

## Results
### Round 1: Trained on 32m offline and 288m online samples (mlp vs simple)
mlp vs sim: 22% trained NOT playing the best card
mlp vs sim: 14% trained playing the best card

*Conclusions*:
- training on 320m "good" samples beats training on 640m "bad" samples
- with good data, it seems training is more effective when not playing the best card

### Round 2: Based on round 1 plus 320m vs simple
mlp vs sim: 32% trained NOT playing the best card both times
mlp vs sim: 22% trained playing the best card both times
**trained with new implementation**
mlp vs sim: 27% trained NOT playing the best card both times; 1 PROCESS
mlp vs sim: 26% trained NOT playing the best card both times; 2 PROCESSES

*Conclusions*:
- training without playing the best card is again better
- the models still improved significantly with additional data

### Round 3: Based on round 2 (NOT best) + 320m samples online
**re-running the mlp-vs-sim with 1 process because the results were strangely very poor**
--> looks like the mlp results weren't better...
mlp vs sim: 14% trained mlp vs mlp (both NOT best)
mlp vs sim: 22% trained mlp vs sim (mlp NOT best)

*Conclusions*:
- the processes don't seem to have an impact on the evaluation

