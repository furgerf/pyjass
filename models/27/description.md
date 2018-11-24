# Sorting decision states
Using encoding 20 from binary data with baseline "better"
4M stored hands initially (better vs better)
Also storing game type decisions
Round: 4M offline from other model in previous round + 4M online
Only using normal parameters
-> ordering by value and sorting the suits

# Round 1
=> 8M hands
10x100: 55.5/46.0%, loss: 6070.1
4x200: 56.0/49.8%, loss: 6077.0

# Round 2
=> 16M hands
10x100: 60.2/58.6%, loss: 5990.5
4x200: 65.9/59.6%, loss: 5830.9

# Round 3
=> 24M hands
10x100: 64.4/60.8%, loss: 6129.5 (was 5866.8 just before!)
4x200: 63.2/63.3%, loss: 5866.3

# Round 4
=> 32M hands
10x100: 67.4/63.2%, loss: 6019.3
4x200: 66.4/66.1%, loss: 5664.0

# Round 5
=> 40M hands
10x100: 65.8/66.5%, loss: 5870.1
4x200: 65.0/66.6%, loss: 5536.0

# Round 6
=> 48M hands
10x100: 69.0/68.4%, loss: 5823.0
4x200: 71.4/68.5%, loss: 5768.9

# Round 7
=> 56M hands
10x100: 69.4/69.1%, loss: 5804.5
4x200: 70.2/69.3%, loss: 5870.9

