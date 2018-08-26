# Sorting decision states
Using encoding 19 from binary data with baseline "better"
4M stored hands initially (better vs better)
Also storing game type decisions
Round: 4M offline from other model in previous round + 4M online
Only using normal parameters
-> ordering by suit and sorting the suits

# Round 1
=> 8M hands
10x100: 56.7/47.6%, loss: 6491.6
4x200: 55.0/52.8%, loss: 5947.8

# Round 2
=> 16M hands
10x100: 58.8/56.8%, loss: 6111.3
4x200: 64.3/63.6%, loss: 5665.6

# Round 3
=> 24M hands
10x100: 55.0/60.8%, loss: 6044.4
4x200: 63.1/66.2%, loss: 5828.8

# Round 4
=> 32M hands
10x100: 64.1/61.2%, loss: 5816.4
4x200: 69.5/68.2%, loss: 5731.1

# Round 5
=> 40M hands
10x100: 67.6/67.1%, loss: 5849.9
4x200: 70.6/69.3%, loss: 5672.9

