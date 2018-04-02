# Relative encoding
Using encoding 11 from binary data
1M stored hands (sim-vs-sim), 1M online
*Data comes from normal models*
*Playing best card during training*
*CODE HAD BUGS, IT WAS THE SAME AS THE PREVIOUS EVAL...*
Storing samples that are played
Using half the normal learning rate, max iter; twice the normal alpha
-> learning\_rate\_init=5e-4,max\_iter=100,alpha=2e-4

100-50-100-50-100: 52.0%, loss: 1823.8
3x100: 43.3%, loss: 1904.8
4x100: 56.1%, loss: 1799.6

## Normal models on same data
100-50-100-50-100: 53.2%, loss: 1796.4
3x100: 53.1%, loss: 1793.8
4x100: 56.7%, loss: 1855.5

# Round two
Training on 3M stored hands (previous round) and 1M online

100-50-100-50-100: 60.7%, loss: 1666.4
3x100: 61.5%, loss: 1665.8
4x100: 64.2%, loss: 1737.7

==> improved by a lot

## Normal models on same data
100-50-100-50-100: 60.2%, loss: 1641.7
3x100: 60.1%, loss: 1705.3
4x100: 65.0%, loss: 1691.9

==> improved by ~7%

# Round three
Training on 3M stored hands (previous round) and 1M online
*From here on, reduce trainingint to 5e4 to see if it's faster when it doesn't need to swap!*
-> this doesn't seem to help...

100-50-100-50-100: 65.5%, loss: 1665.4
3x100: %, loss: aborted
4x100: %, loss: aborted

==> aborted

## Normal models on same data
100-50-100-50-100: 67.4%, loss: 1661.0
3x100: 63.5%, loss: 1683.1
4x100: 64.7%, loss: 1651.4

==> improved, but inconsistently

# Round four
Training on 3M stored hands (previous round) and 1M online

## Normal models on same data
100-50-100-50-100: 67.0%, loss: 1634.0
3x100: 65.6%, loss: 1685.2
4x100: 62.9%, loss: 1626.3

==> seems to be stagnating

# Round five
Training on 3M stored hands (previous round) and 1M online

## Normal models on same data
100-50-100-50-100: 68.7%, loss: 1643.9
3x100: 64.7%, loss: 1685.9
4x100: 66.1%, loss: 1588.2

==> 100-50-100-50-100 might still improve but the others seem to stagnate


# CONCLUSIONS
- The performance stops improving significantly after ~10M hands
- There isn't much difference among the models
- Fancy parameters don't really seem to change anything
- The models are still very inconsistent

