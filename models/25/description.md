# Grouping cards by suit
Using encoding 18 from binary data with baseline "better"
4M stored hands initially (better vs better)
Also storing game type decisions
Round: 4M offline from other model in previous round + 4M online
Only using normal parameters
-> ordering by suit

# Round 1
=> 8M hands
10x100: 42.6/39.1%, loss: 6472.0
4x200: 58.5/51.1%, loss: 5912.6
5x200: 36.9/35.3%, loss: 5705.9
3x300: 40.4/35.9%, loss: 5700.2

# Round 2
=> 16M hands
10x100: 55.8/51.7%, loss: 6277.4
4x200: 71.2/66.2%, loss: 5936.1
5x200: 41.5/41.6%, loss: 5579.1
3x300: 40.1/41.7%, loss: 5528.0

# Round 3
=> 24M hands
10x100: 59.1/53.8%, loss: 6111.9
4x200: 72.6/72.6%, loss: 5744.4
5x200: 42.5/45.4%, loss: 5413.3
3x300: 40.6/43.5%, loss: 5389.2

# Round 4
=> 32M hands
10x100: 64.4/63.7%, loss: 5891.6
4x200: 75.7/74.8%, loss: 5665.9
5x200: 42.5/45.1%, loss: 5292.1
3x300: 40.6/42.7%, loss: 5190.9

# Round 5
=> 40M hands
10x100: 68.9/67.3%, loss: 5903.0
4x200: 75.9/74.9%, loss: 5635.0

