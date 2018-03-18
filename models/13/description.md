# Trying to see if learning actually works
Using "default" encoding (5)
Default values training int 1e5, procs 2; alpha 1e-4

# Stage 1: Initial training
BS 1e2: 26.9%
BS 1e3: 27.3%
BS 1e4: 24.2%
alpha 1e-2: 21.8% (starting from scratch)
alpha 1e-2: 21.3% (starting from mlp)
max\_iter 10: %
-> "normal" training time is around 12-13 hours

new architectures:
2x2 hidden: 0.7%
3x3 hidden: 1.1%
20x10 hidden: 6% (training time: 19h45), loss: 850.6
30x10 hidden: aborted (narrow layers don't work)

## 200 neurons
2x100 hidden: 49.5% (training time: 17h), loss: 694.4

## 300 neurons
training times are without time of training on stored data
1x300 hidden: 31.9% (training time: 17h30), loss: 803.1
2x150 hidden: 53.7% (training time: 21h15), loss: 678.4
3x100 hidden: 62.5% (training time: 21h), loss: 653.4

## 400 neurons
training times are without time of training on stored data
2x200 hidden: 56.6% (training time: 29h15), loss: 669.9
4x100 hidden: 64.9% (training time: 32h30), loss: 635.8
8x50 hidden: 54.4% (training time: 31h), loss: 687.1

## 500 neurons
training times are without time of training on stored data
5x100 hidden: 61.9% (training time: 34h30), loss: 651.9

# Stage 2: Online training
(ignore this)
BS 1e2: 24.5%
BS 1e3: 27.7%
BS 1e4: 22.4%
