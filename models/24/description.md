# Cost focuses even more on hand result
Using encoding 17 from binary data with baseline "better"
4M stored hands initially (better vs better)
Round: 4M offline from other model in previous round + 4M online
-> longer rounds
Playing best card during training
Storing samples that are played
Only using normal parameters
-> ordering by value

# Round 1
=> 8M hands
6x100: 49.3/41.6%, loss: 6257.8
7x100: 46.7/41.0%, loss: 6323.2
8x100: 52.9/44.1%, loss: 6348.1
9x100: 52.8/42.8%, loss: 6189.6
5x200: 58.4/50.2%, loss: 6075.0
5x200-spades: 38.6/36.0%, loss: 5487.4
3x300: 61.0/54.3%, loss: 5866.6
3x300-spades: 34.9/35.4%, loss: 5897.4 <-- had to re-start from round-0

# Round 1.5
=> 8M hands
4x200: 56.7/49.6%, loss: 5892.5
4x200-unnenufe: 55.8/53.9%, loss: 5919.6

# Round 2
=> 16M hands
6x100: 58.1/55.5%, loss: 6240.4
7x100: 55.0/55.5%, loss: 6088.8
8x100: 61.6/58.8%, loss: 5813.0
9x100: 57.5/56.7%, loss: 5829.1
5x200: 65.7/64.9%, loss: 5932.3
5x200-spades: 43.2/42.9%, loss: 5291.4
3x300: 70.8/66.2%, loss: 5799.4
3x300-spades: 40.8/41.2%, loss: 5396.6

# Round 2.5
=> 16M hands
4x200: 71.6/64.1%, loss: 5960.0
4x200-unnenufe: 73.1/66.1%, loss: 5943.7

# Round 3
=> 24M hands
6x100: 60.6/59.8%, loss: 5936.8
7x100: 62.5/63.5%, loss: 5861.3
8x100: 67.3/64.9%, loss: 5780.9
9x100: 66.5/63.8%, loss: 5927.9
5x200: 67.8/67.7%, loss: 5734.4
5x200-spades: 41.4/44.3%, loss: 5201.4
3x300: 70.8/70.0%, loss: 5706.6
3x300-spades: 41.4/41.7%, loss: 5529.4

# Round 3.5
=> 24M hands
4x200: 72.9/70.4%, loss: 5841.3
4x200-unnenufe: 69.2/71.5%, loss: 5669.0

# Round 4
=> 32M hands
6x100: 62.0/62.4%, loss: 5999.2
7x100: 68.2/67.3%, loss: 5870.2
8x100: 68.0/66.7%, loss: 5743.5
9x100: 68.8/68.1%, loss: 5705.5
5x200: 69.8/69.7%, loss: 5711.3
5x200-spades: 42.9/45.0%, loss: 5166.0
3x300: 75.1/71.6%, loss: 5646.1
3x300-spades: 45.9/43.5%, loss: 5452.0

# Round 4.5
=> 32M hands
4x200: 74.7/72.6%, loss: 5834.5
4x200-unnenufe: 72.2/74.1%, loss: 5655.0

# Round 5
=> 40M hands
6x100: 62.9/64.2%, loss: 5810.7
7x100: 69.6/68.8%, loss: 5989.7
8x100: 72.6/69.6%, loss: 5879.2
9x100: 71.5/71.0%, loss: 5876.3
5x200: 71.7/71.8%, loss: 5663.1
5x200-spades: 41.9/45.2%, loss: 5226.8
3x300: 75.2/73.0%, loss: 5729.7
3x300-spades: 45.4/43.9%, loss: 5243.6

# Round 5.5
=> 40M hands
4x200: 75.1/74.2%, loss: 5721.8

# Round 6
=> 48M hands
6x100: 65.7/65.8%, loss: 5763.1
7x100: 71.1/70.4%, loss: 5773.8
8x100: 71.1/70.9%, loss: 5767.1
9x100: 70.3/72.0%, loss: 5926.9
5x200: 72.8/73.1%, loss: 5735.3
5x200-spades: 43.1/45.3%, loss: 5215.3
3x300: 71.7/74.9%, loss: 5730.5
3x300-spades: 43.3/44.0%, loss: 4993.5

# Round 6.5
=> 52M hands
4x200: 76.3/74.9%, loss: 5719.7

# Round 7
=> 56M hands
6x100: 70.6/67.2%, loss: 5866.8
7x100: 69.5/70.6%, loss: 5892.2
8x100: 72.9/71.5%, loss: 5811.9
9x100: 73.3/73.6%, loss: 5870.2
5x200: 73.3/74.1%, loss: 5649.2
3x300: 78.2/75.5%, loss: 5639.6

# Round 7.5
=> 60M hands
4x200: 76.2/75.6%, loss: 5621.0

# Round 8
=> 64M hands
6x100: 70.1/68.7%, loss: 5730.7
7x100: 72.2/72.0%, loss: 5717.9
8x100: 73.8/72.4%, loss: 5816.8
9x100: 75.3/74.6%, loss: 5978.2

# Round 8.5
=> 68M hands
4x200: 75.7/75.7%, loss: 5559.8

# Round 9
=> 72M hands
6x100: 69.9/69.5%, loss: 5814.4
7x100: 73.8/72.2%, loss: 6003.0
8x100: 71.2/73.1%, loss: 5739.0
9x100: 74.8/75.3%, loss: 5954.5

# Round 10
=> 80M hands
6x100: 68.6/69.5%, loss: 5847.2
7x100: 74.5/72.7%, loss: 5947.3
8x100: 75.6/73.8%, loss: 5713.0
9x100: 76.0/75.1%, loss: 5885.7

