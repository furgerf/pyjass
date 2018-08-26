# Team-mate highlighting
Using encoding 15 from binary data with baseline "better"
2M stored hands initially (better vs better)
Round: 2M offline from other model in previous round + 2M online
Playing best card during training
Storing samples that are played
Only using normal parameters
Also training the 6x100-model on 6x100-data+online to see if the result is better
when only seeing "own" data
Also training wider models (4x200, 300-200-300 -> same # of weights) only on own data

# Round 1
=> 4M hands
6x100: 40.4/35.4%, loss: 1660.2
7x100: 38.7/35.3%, loss: 1690.4

# Round 1.5
=> 6M hands
6x100: 48.2/48.1%, loss: 1597.4
4x200: 56.0/46.7%, loss: 1572.9
300-200-300: 55.0/49.6%, loss: 1567.4

# Round 2
=> 8M hands
6x100: 56.1/52.2%, loss: 1552.0
7x100: 52.0/50.3%, loss: 1624.6

# Round 2.5
=> 10M hands
6x100: 55.7/55.1%, loss: 1537.4
4x200: 61.6/58.6%, loss: 1544.0
300-200-300: 62.4/60.5%, loss: 1534.2

# Round 3
=> 12M hands
6x100: 57.3/56.3%, loss: 1509.9
7x100: 57.6/55.1%, loss: 1561.2

# Round 3.5
=> 14M hands
6x100: 58.2/57.0%, loss: 1510.6
4x200: 64.7/62.6%, loss: 1535.9
300-200-300: 63.9/62.5%, loss: 1485.9

# Round 4
=> 16M hands
6x100: 58.3/58.5%, loss: 1563.5
7x100: 58.8/60.0%, loss: 1535.9

# Round 4.5
=> 18M hands
6x100: 60.2/59.2%, loss: 1502.3
4x200: 67.1/66.1%, loss: 1490.5
300-200-300: 66.6/63.9%, loss: 1490.3

# Round 5
=> 20M hands
6x100: 60.9/60.0%, loss: 1508.1
7x100: 65.6/63.0%, loss: 1525.4

# Round 5.5
=> 22M hands
6x100: 60.3/61.1%, loss: 1502.6
4x200: 67.1/67.2%, loss: 1458.3
300-200-300: 67.9/65.5%, loss: 1444.6

# Round 6
=> 24M hands
6x100: 65.2/62.3%, loss: 1498.1
7x100: 65.9/64.0%, loss: 1531.7

# Round 6.5
=> 26M hands
6x100: 65.0/62.5%, loss: 1511.5
4x200: 68.4/67.9%, loss: 1462.7
300-200-300: 66.8/67.1%, loss: 1465.8

# Round 7
=> 28M hands
6x100: 63.8/63.6%, loss: 1476.6
7x100: 64.0/64.3%, loss: 1560.3

# Round 7.5
=> 30M hands
6x100: 67.4/64.3%, loss: 1496.4
4x200: 69.1/69.3%, loss: 1460.9
300-200-300: 68.6/67.2%, loss: 1445.1

# Round 8
=> 32M hands
6x100: 66.1/65.1%, loss: 1496.7
7x100: 66.7/65.1%, loss: 1509.3

# Round 8.5
=> 34M hands
6x100: 66.2/65.3%, loss: 1485.5
4x200: 69.3/69.9%, loss: 1444.6
300-200-300: 68.3/68.2%, loss: 1461.8

# Round 9
=> 36M hands
6x100: 68.5/66.8%, loss: 1481.6
7x100: 65.6/65.3%, loss: 1523.0

# Round 9.5
=> 38M hands
6x100: 66.8/66.4%, loss: 1490.4
4x200: 72.2/70.5%, loss: 1457.7
300-200-300: 66.9/68.2%, loss: 1433.9

# Round 10
=> 40M hands
6x100: 67.3/67.9%, loss: 1500.9
7x100: 68.9/65.8%, loss: 1495.3

# Round 10.5
=> 42M hands
6x100: 66.7/67.3%, loss: 1485.8
4x200: 68.7/70.9%, loss: 1446.0
300-200-300: 69.7/68.5%, loss: 1466.5

# Round 11
=> 44M hands
6x100: 69.4/67.7%, loss: 1483.9
7x100: 68.9/66.4%, loss: 1525.9 (was 1493.3 just before!!)

# Round 11.5
=> 46M hands
6x100: 69.7/66.9%, loss: 1494.5
4x200: 71.4/71.0%, loss: 1452.5

# Round 12
=> 48M hands
6x100: 69.3/68.8%, loss: 1479.5
7x100: 69.4/67.5%, loss: 1491.9

# Round 12.5
=> 50M hands
6x100: 68.0/67.8%, loss: 1498.9
4x200: 69.5/72.3%, loss: 1425.2

# Round 13
=> 52M hands
6x100: 68.3/69.1%, loss: 1483.8
7x100: 68.2/67.7%, loss: 1511.9

# Round 13.5
=> 54M hands
6x100: 68.6/68.6%, loss: 1468.9
4x200: 72.4/72.4%, loss: 1449.8

# Round 14
=> 56M hands
6x100: 68.8/70.0%, loss: 1473.0
7x100: 67.6/68.0%, loss: 1504.6

# Round 14.5
=> 58M hands
6x100: 70.0/68.8%, loss: 1475.6
4x200: 71.6/72.9%, loss: 1438.9

# Round 15
=> 62M hands
6x100: 69.2/69.4%, loss: 1461.6
7x100: 69.3/68.5%, loss: 1487.0

# Round 15.5
=> 64M hands
6x100: 71.5/69.3%, loss: 1459.4
4x200: 73.1/73.0%, loss: 1435.3

