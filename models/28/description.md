# Sorting decision states
Using encoding 21 from binary data with baseline "better"
4M stored hands initially (better vs better)
Also storing game type decisions
Round: 4M offline from other model in previous round + 4M online
Only using normal parameters
Highlighting trump cards with offset, playing trump spades

# Round 1
=> 8M hands
5x200: 39.1/33.9%, loss: 5840.6
3x300: 35.7/33.9%, loss: 5767.4

# Round 2
=> 16M hands
5x200: 43.1/40.0%, loss: 5582.4
3x300: 37.1/40.0%, loss: 5412.6

# Round 3
=> 24M hands
5x200: 37.0/42.2%, loss: 5459.5
3x300: 41.5/40.3%, loss: 5433.5

# Round 4
=> 32M hands
5x200: 38.9/41.7%, loss: 5621.7
3x300: 42.1/41.1%, loss: 5508.8

