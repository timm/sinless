#!/usr/bin/env python3.9
from sinless import *
eg = Eg.one

@eg  
def fails(my): 
 "test if fails are caught"
 print("Can my test engine catch fails?")
 assert 1/0

@eg
def show(my): 
  "Show default config, updated with any command-line flags"
  print(my)

@eg
def works(my): 
  "test if anything works at all"
  assert True

@eg
def sym(my):
  "check symbol code"
  s = Sym()
  for x in "aaaabb": s.add(x)
  print(s.has)

@eg
def num(my):
  "check num"
  n=Num()
  for _ in range(10000): n.add(int(100*r()))
  print(n.all()[::20])

@eg
def numDist(my):
  "check num dist"
  n=Num()
  for _ in range(10000): n.add(int(100*r()))
  print(n.dist("?",20))

@eg
def sample(my):
  "can i sample from disc?"
  s = Sample(my).load("data/auto93.csv")
  print(s.x[1])
  print([(c.txt,c.w) for c in s.y])

@eg
def dist(my):
  "Looking for faraway things"
  s = Sample(my).load("data/auto93.csv")
  random.shuffle(s.rows)
  for row1 in s.rows[:10]:
    c,row2 = s.faraway(row1,s.rows)
    print("")
    print(row1.cells)
    print(row2.cells,int(100*c))

@eg
def cluster(my):
  "cluster stuff"
  s = Sample(my).load("data/auto93.csv")
  for clus in sorted(s.cluster()):
    print(clus.ys())

def _discrete(my,f="data/auto93.csv"):
  "distinguish good and bad clusters"
  s = Sample(my).load(f)
  clusters = sorted(s.cluster())
  worst, best = clusters[0], clusters[-1], 
  for good,bad in zip(best.x,worst.x):
    pre="\n"
    for d in  good.discretize(bad, my):
      print(pre,end=""); pre=""
      print(d)
  print("")
  [print("best", r.cells) for r in best.rows]
  print("")
  [print("worst", r.cells) for r in worst.rows]

@eg
def dcAuto93(my):
  "distinguish good and bad clusters"
  _discrete(my,"data/auto93.csv")

@eg
def dcAuto2(my):
  "distinguish good and bad clusters"
  _discrete(my,"data/auto2.csv")
    
@eg
def egfft(my):
  s = Sample(my).load("data/auto93.csv")
  Fft(s,my)
  
Eg.run()
