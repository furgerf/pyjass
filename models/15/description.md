# New cost: 4\*round+1\*hand
Using encoding 8 from binary data
3M stored hands (sim-vs-sim), 3M online

3x100: 49.1%, loss: 2249.5 (training time: 11h30) <= looks fairly bad and extremely inconsistent
4x100: 50.2%, loss: 2168.7 (training time: 14h30) <= dito
100,50,100,50: 46.8%, loss: 2213.7 (training time: 13h) <= dito

# Round two
Doing another 3M online hands
Trying to see if this really is it...

3x100: 54.7%, loss: 2189.2 (training time: 8h) <= improved significantly
4x100: 55.9%, loss: 2154.4 (training time: 9h45) <= dito
100,50,100,50: 53.3%, loss: 2196.6 (training time: 8h) <= dito

# Round three
Using another 3M online

3x100: 54.5%, loss: 2178.3 (training time: 9h45) <= looks like it's done
4x100: 56.1%, loss: 2148.8 (training time: 11h) <= dito
100,50,100,50: 59.0%, loss: 2213.1 (training time: 9h45) <= might actually still kinda improve...

# Round four
Using another 3M online

100,50,100,50: 54.4%, loss: 2158.7 (training time: 9h45) <= the previous good result must've been down to luck

