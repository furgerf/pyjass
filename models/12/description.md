# Trying to find factors that impact learning performance
Based on model "08/mlp-simple-best-round-2.pkl" [[or mlp-round-3-vs-simple.pkl]] (trained on 640M [[960M]] samples and the default values:
- training int 1e5
- batch size 1e3
- parallel processes 2

- batch\_size ("minibatch") 200
- learning\_rate\_init 1e-3
- max\_iter 200
- alpha 1e-4
- early stopping false
- solver adam

## Baseline
- original model: 22%
- default training: 28.3% (training time: 13h35)
- *default training with new implementation*: 28.5%

## Training int
- 1e4: 23.8% (training time: 13h40)
- 2e5: 24.2% (training time: 13h48-24+42=14h) <- this crashed at 95%, the remaining hands were trained afterwards

## Batch size
- 1e2: 29.4% (training time: 13h35)
- 1e4: 27.0% (training time: 13h40)

## Parallel processes
- trained on 1: 23.9% (training time: 24h30/2=12h15)
- trained on 4: 25.0% (training time: 6h45\*2=14h30)
- trained on 5: 27.0% (training time: 5h30\*2.5=13h45)

## Playing best card
- true: 19.4% (training time: 12h30)

## batch\_size (minibatch)
- 160: 27.7% (training time: 13h45)
- 320: 28.7% (training time: 13h30)

## learning\_rate\_init
- 1e-2: 28.4% (training time: 14h)
- 1e-4: 28.4% (training time: 13h50)
(exact same results)

## max\_iter
- 100: 25.4% (training time: 13h)
- 500: 25.4% (training time: 12h50)
(exact same results)

