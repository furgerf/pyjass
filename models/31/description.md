# Using fixed better baseline
Using encoding 23 from binary data with baseline "fixed-better"
4M stored hands initially (fixed-better vs fixed-better)
Also storing game type decisions
Round: 4M offline from other model in previous round + 4M online
Only using normal parameters

# Round 1
=> 8M hands
5x200: 40.0/34.9%, loss: 5613.8 (vs simple: 49.6%)
3x300: 42.4/36.3%, loss: 5690.2 (vs simple: 54.4%)
5x100: 31.0/29.6%, loss: 6220.0 (vs simple: 42.3%)
2x200: 33.6/28.7%, loss: 6152.4 (vs simple: 43.3%)
6x300: 40.7/37.3%, loss: 5337.1 (vs simple: 49.8%)
4x400: 44.3/38.2%, loss: 5483.3 (vs simple: 54.8%)
5x200-keras: 31.7/31.6%, loss: 12046.9 (vs simple: 43.2%)
3x300-keras: 29.8/28.7%, loss: 12181.4 (vs simple: 39.4%)
6x300-keras: 34.5/32.1%, loss: 11506.8 (vs simple: 47.1%)
4x400-keras: 31.1/32.9%, loss: 11394.8 (vs simple: 39.8%)
8x600-keras: 1.7/1.7%, loss: 124734.2 (vs simple: 1.6%)
6x700-keras: 31.5/31.1%, loss: 12113.6 (vs simple: 43.5%)

# Round 2
=> 16M hands
5x200: 42.7/42.7%, loss: 5313.3 (vs simple: 51.0%)
3x300: 40.6/42.4%, loss: 5343.6 (vs simple: 50.4%)
5x100: 35.4/35.4%, loss: 5693.2 (vs simple: 48.4%)
2x200: 37.1/34.3%, loss: 6013.0 (vs simple: 51.1%)
6x300: 45.8/45.7%, loss: 4960.8 (vs simple: 54.3%)
4x400: 43.9/42.9%, loss: 5002.0 (vs simple: 53.2%)
5x200-keras: 38.0/36.5%, loss: 11457.9 (vs simple: 48.2%)
3x300-keras: 34.6/35.1%, loss: 11440.9 (vs simple: 43.3%)
6x300-keras: 34.8/36.9%, loss: 11879.2 (vs simple: 45.8%)
4x400-keras: 38.8/40.1%, loss: 11819.2 (vs simple: 49.0%)
8x600-keras: /%, loss:  (vs simple: %)
6x700-keras: /%, loss:  (vs simple: %)

# Round 3
=> 20M hands
5x200: 42.8/44.7%, loss: 5082.6 (vs simple: 49.9%)
3x300: 38.3/43.3%, loss: 5165.2 (vs simple: 47.9%)
5x100: 36.2/37.4%, loss: 5632.1 (vs simple: 46.2%)
2x200: 35.8/35.5%, loss: 5685.1 (vs simple: 47.5%)
6x300: 45.6/46.4%, loss: 4897.9 (vs simple: 53.9%)
4x400: 44.7/44.5%, loss: 4812.2 (vs simple: 53.2%)
5x200-keras: 37.2/37.1%, loss: 11401.3 (vs simple: 49.0%)
3x300-keras: 36.5/36.8%, loss: 11141.9 (vs simple: 45.4%)
6x300-keras: 42.4/38.3%, loss: 11221.7 (vs simple: 53.5%)
4x400-keras: 35.7/40.8%, loss: 10801.3 (vs simple: 41.9%)
8x600-keras: /%, loss:  (vs simple: %)
6x700-keras: /%, loss:  (vs simple: %)

# Round 4
=> 24M hands
5x200: 40.8/45.5%, loss: 4885.6 (vs simple: 49.4%)
3x300: 43.6/44.3%, loss: 5153.8 (vs simple: 52.9%)
5x100: 38.5/39.4%, loss: 5531.3 (vs simple: 51.5%)
2x200: 40.1/37.7%, loss: 5675.4 (vs simple: 52.7%)
6x300: 50.6/48.5%, loss: 4842.2 (vs simple: 61.3%)
4x400: 48.5/45.6%, loss: 4835.4 (vs simple: 58.3%)
5x200-keras: 37.6/39.0%, loss: 11171.1 (vs simple: 47.6%)
3x300-keras: 40.9/36.8%, loss: 10996.2 (vs simple: 51.9%)
6x300-keras: 41.4/39.1%, loss: 11156.4 (vs simple: 53.0%)
4x400-keras: 43.2/41.2%, loss: 10637.3 (vs simple: 54.6%)
8x600-keras: /%, loss:  (vs simple: %)
6x700-keras: /%, loss:  (vs simple: %)

# Round 5
=> 32M hands
6x300: /%, loss:  (vs simple: %)
4x400: /%, loss:  (vs simple: %)
5x200-keras: 39.7/39.5%, loss: 11231.9 (vs simple: 51.0%)
3x300-keras: 35.6/38.0%, loss: 10954.1 (vs simple: 42.7%)
6x300-keras: 44.0/39.4%, loss: 11045.3 (vs simple: 55.8%)
4x400-keras: 40.9/42.6%, loss: 10449.3 (vs simple: 49.8%)
8x600-keras: /%, loss:  (vs simple: %)
6x700-keras: /%, loss:  (vs simple: %)

