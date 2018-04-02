# New cost: 2\*round+1\*hand
Using encoding 9 from binary data
3M stored hands (sim-vs-sim), 3M online

3x100: 57.8%, loss: 1018.0 (training time: 10h30) <= looks ok-ish, might improve
4x100: 56.8%, loss: 997.4 (training time: 14h) <= looks ok-ish, might improve
100,50,100,50: 61.4%, loss: 1014.2 (training time: 12h15) <= looks decent, kind-of likely to improve!

# Round two
Using another 3M online

3x100: 63.3%, loss: 1007.0 (training time: 7h30) <= hard to say, may improve
4x100: 63.0%, loss: 981.5 (training time: 8h) <= hard to say, may improve
100,50,100,50: 61.1%, loss: 998.8 (training time: 7h30) <= hard to say, may improve

# Round three
Using another 3M online

3x100: 58.5%, loss: 997.3 (training time: 10h15) <= looks like it's done learning now
4x100: 62.2%, loss: 986.4 (training time: 10h) <= looks like it's done learning now
100,50,100,50: 60.4%, loss: 993.9 (training time: 10h) <= looks like it's done learning now

# Round four
Using another 3M online
Just trying to see if it's really done...

4x100: 62.7%, loss: 986.0 (training time: 7h45) <= really seems to be done

# Complex model
Trying layers 100 50 200 50 200 50 100 to see if something like that might help
Doing the entire Training in one go; 3M offline + 9M online

59.7%, loss: 1003.2 (training time: 59h) <= no use...

