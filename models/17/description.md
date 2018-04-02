# New cost: 1\*round+2\*hand
Using encoding 10 from binary data
2M stored hands (sim-vs-sim), 2M online
*Playing best card during training*
Storing samples that are played
Using half the normal learning rate, max iter; twice the normal alpha
-> learning\_rate\_init=5e-4,max\_iter=100,alpha=2e-4

100-50-100-50-100: 60.5%, loss: 1687.6
3x100: 58.6%, loss: 1723.6
4x100: 63.1%, loss: 1789.9

## Normal models on same data
100-50-100-50-100: 61.3%, loss: 1722.4
3x100: 55.8%, loss: 1718.8
4x100: 66.2%, loss: 1716.9

==> normal is similar to fancy

# Round two
Training on 6M stored hands (previous round) and 2M online

100-50-100-50-100: 65.3%, loss: 1637.7
3x100: 63.6%, loss: 1672.1
4x100: 68.1%, loss: 1585.5

==> improved consistently by ~5%

## Normal models on same data
100-50-100-50-100: 66.4%, loss: 1683.1
3x100: 63.8%, loss: 1638.6
4x100: 68.2%, loss: 1662.0

==> improved by ~5%; normal is similar to fancy

# Round three
Training on 6M stored hands (previous round) and 2M online

100-50-100-50-100: 65.9%, loss: 1607.4
3x100: 60.5%, loss: 1612.6
4x100: 66.7%, loss: 1565.1

==> stagnated

## Normal models on same data
100-50-100-50-100: 65.3%, loss: 1645.9
3x100: 63.6%, loss: 1643.9
4x100: 69.4%, loss: 1624.7

==> stagnated; normal is similar to fancy

