# Cost focuses on round result
Using encoding 16 from binary data with baseline "better"
4M stored hands initially (better vs better)
Round: 4M offline from other model in previous round + 4M online
-> longer rounds
Playing best card during training
Storing samples that are played
Only using normal parameters
Also training a wide model (4x200) only on own data

# Round 1
=> 8M hands
6x100: 45.7/44.6%, loss: 624.0
7x100: 51.8/43.9%, loss: 654.5

# Round 1.5
=> 12M hands
4x200: 60.6/54.2%, loss: 570.3

# Round 2
=> 16M hands
6x100: 61.1/56.7%, loss: 582.7
7x100: 60.2/56.8%, loss: 605.7

# Round 2.5
=> 20M hands
4x200: 66.3/62.3%, loss: 535.4

# Round 3
=> 24M hands
6x100: 63.4/60.7%, loss: 570.8
7x100: 61.5/61.7%, loss: 571.8

# Round 3.5
=> 28M hands
4x200: 66.2/65.2%, loss: 517.1

# Round 4
=> 32M hands
6x100: 64.6/62.8%, loss: 560.2
7x100: 65.7/64.2%, loss: 551.8

# Round 4.5
=> 36M hands
4x200: 69.5/66.5%, loss: 511.4

# Round 5
=> 40M hands
6x100: 63.4/63.5%, loss: 549.4
7x100: 66.0/65.1%, loss: 555.8

# Round 5.5
=> 44M hands
4x200: 70.1/67.6%, loss: 510.7

# Round 6
=> 48M hands
6x100: 62.8/64.4%, loss: 546.1
7x100: 66.7/66.2%, loss: 560.2

# Round 6.5
=> 52M hands
4x200: 70.9/67.5%, loss: 513.3

# Round 7
=> 56M hands
6x100: 63.0/65.1%, loss: 557.1
7x100: 65.2/65.8%, loss: 554.4

# Round 7.5
=> 60M hands
4x200: 71.2/68.4%, loss: 505.2

# Round 8
=> 64M hands
6x100: 66.5/65.0%, loss: 543.4
7x100: 65.8/66.7%, loss: 537.4

# Round 8.5
=> 68M hands
4x200: 68.4/68.4%, loss: 506.1

# Round 9
=> 72M hands
6x100: 61.6/65.1%, loss: 549.2
7x100: 67.7/66.9%, loss: 541.1

# Round 9.5
=> 76M hands
4x200: 70.2/69.0%, loss: 507.3

# Round 10
=> 80M hands
6x100: 67.6/65.3%, loss: 544.4
7x100: 68.9/67.2%, loss: 542.2

# Round 10.5
=> 84M hands
4x200: 68.7/69.3%, loss: 502.8

