# Cost focuses even more on hand result
Using encoding 17 from binary data with baseline "better"
4M stored hands initially (better vs better)
Round: 4M offline from other model in previous round + 4M online
-> longer rounds
Playing best card during training
Storing samples that are played
Only using normal parameters
when only seeing "own" data
Also training a wide model (4x200) only on own data

# Round 1
=> 8M hands
6x100: 49.3/41.6%, loss: 6257.8
7x100: 46.7/41.0%, loss: 6323.2
8x100: 52.9/44.1%, loss: 6348.1
9x100: 52.8/42.8%, loss: 6189.6

# Round 1.5
=> 12M hands
6x100: /%, loss: 
4x200: 56.7/49.6%, loss: 5892.5

# Round 2
=> 16M hands
6x100: 58.1/55.5%, loss: 6240.4
7x100: 55.0/55.5%, loss: 6088.8
8x100: 61.6/58.8%, loss: 5813.0
9x100: 57.5/56.7%, loss: 5829.1

# Round 2.5
=> 20M hands
6x100: /%, loss: 
4x200: 71.6/64.1%, loss: 5960.0

# Round 3
=> 24M hands
6x100: 60.6/59.8%, loss: 5936.8
7x100: 62.5/63.5%, loss: 5861.3
8x100: 67.3/64.9%, loss: 5780.9
9x100: 66.5/63.8%, loss: 5927.9

# Round 3.5
=> 28M hands
6x100: /%, loss: 
4x200: /%, loss: 

# Round 4
=> 32M hands
6x100: 62.0/62.4%, loss: 5999.2
7x100: 68.2/67.3%, loss: 5870.2
8x100: 68.0/66.7%, loss: 5743.5
9x100: 68.8/68.1%, loss: 5705.5

# Round 4.5
=> 36M hands
6x100: /%, loss: 
4x200: /%, loss: 

# Round 5
=> 40M hands
6x100: 62.9/64.2%, loss: 5810.7
7x100: 69.6/68.8%, loss: 5989.7
8x100: /%, loss: 
9x100: /%, loss: 

# Round 5.5
=> 44M hands
6x100: /%, loss: 
4x200: /%, loss: 

# Round 6
=> 48M hands
6x100: 65.7/65.8%, loss: 5763.1
7x100: 71.1/70.4%, loss: 5773.8
8x100: /%, loss: 
9x100: /%, loss: 

# Round 6.5
=> 52M hands
6x100: /%, loss: 
4x200: /%, loss: 

# Round 7
=> 56M hands
6x100: 70.6/67.2%, loss 5866.8
7x100: 69.5/70.6%, loss: 5892.2
8x100: /%, loss: 
9x100: /%, loss: 

# Round 7.5
=> 60M hands
6x100: /%, loss: 
4x200: /%, loss: 

# Round 8
=> 64M hands
6x100: 70.1/68.7%, loss: 5730.7
7x100: 72.2/72.0%, loss: 5717.9
8x100: /%, loss: 
9x100: /%, loss: 

# Round 8.5
=> 68M hands
6x100: /%, loss: 
4x200: /%, loss: 

# Round 9
=> 72M hands
6x100: 69.9/69.5%, loss: 5814.4
7x100: 73.8/72.2%, loss: 6003.0
8x100: /%, loss: 
9x100: /%, loss: 

# Round 9.5
=> 76M hands
6x100: /%, loss: 
4x200: /%, loss: 

# Round 10
=> 80M hands
6x100: 68.6/69.5%, loss: 5847.2
7x100: 74.5/72.7%, loss: 5947.3
8x100: /%, loss: 
9x100: /%, loss: 

# Round 10.5
=> 84M hands
6x100: /%, loss: 
4x200: /%, loss: 

