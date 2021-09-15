from sinless import *

class Eg:
  crash = -1
  def fails(my): 
   "test if fails are caught"
   assert 1/0

  def list(my):
    "list all examples"
    for s,f in vars(Eg).items():
      if type(f) == fun:
        if s[0] !="_":
          print(f"  {s:>15} : {f.__doc__ or ''}")

  def show(my): 
    "Show default config, updated with any command-line flags"
    print(my)

  def works(my): 
    "test if anything works at all"
    assert True

  def _noop(my):  
    "do nothing"
    return 1

  def sym(my):
    "check symbol code"
    s=Sym()
    for x in "aaaabb": s.add(x)
    print(s.has)

  def num(my):
    "check num"
    n=Num()
    for _ in range(10000): n.add(int(100*r()))
    print(n.all())

  def numDist(my):
    "check num dist"
    n=Num()
    for _ in range(10000): n.add(int(100*r()))
    print(n.dist("?",20))

  def sample(my):
    "can i sample from disc?"
    s=Sample(my).load("../data/auto93.csv")
    print(s.x[1])
    print([(c.txt,c.w) for c in s.y])

  def dist(my):
    "Looking for faraway things"
    s=Sample(my).load("../data/auto93.csv")
    random.shuffle(s.rows)
    for row1 in s.rows[:10]:
      c,row2 = s.faraway(s.rows,row1)
      print("")
      print(row1.cells)
      print(row2.cells,int(100*c))

  def cluster(my):
    "cluster stuff"
    s=Sample(my).load("../data/auto93.csv")
    for clus in sorted(s.cluster()):
      print(clus.ys())

  def _discrete(my,f="../data/auto93.csv"):
    "distinguish good and bad clusters"
    s=Sample(my).load(f)
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

  def dcAuto93(my):
    "distinguish good and bad clusters"
    my.depth=6
    Eg._discrete(my,"../data/auto93.csv")

  def dcAuto2(my):
    "distinguish good and bad clusters"
    my.depth=5
    Eg._discrete(my,"../data/auto2.csv")
       
main(Eg)
sys.exit(Eg.crash)
