from types import FunctionType as fun
import sys,traceback
from sinless import *
from cli import cli

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
    #my.depth=6
    Eg._discrete(my,"../data/auto93.csv")

  def dcAuto2(my):
    "distinguish good and bad clusters"
    my.depth=5
    Eg._discrete(my,"../data/auto2.csv")
       
def _main(todo=Eg._noop, egs={}):
  """(1) Update the config using any command-line settings.
  (2) Maybe, udpate  `todo` from the  command line."""    
  my = o(**cli("python3 range.py [OPTIONS]"))
  if my.Todo:
    Eg.list(my)
  else:
    if my.todo == "all":
      for k,f in egs.items():
        if type(f) == fun and k[0] != "_":
          _one(my, f)
      print("Errors:",Eg.crash)
    else:
      _one(my, egs[my.todo] if my.todo else todo)
  
def _one(my, todo):
  """(1) Initialize the random number seed.
  (2) Call function `todo`, passing in the updated config."""
  random.seed(my.seed)
  w = sys.stderr.write
  def _red(  msg): w(f"\x1b[1;31m✘ {msg}\x1b[0m\n")
  def _green(msg): w(f"\x1b[1;32m✔ {msg}\x1b[0m\n")
  try: 
    todo(my)
    _green(todo.__name__)
  except Exception as err:
    Eg.crash += 1
    _red(todo.__name__)
    if my.loud: print(traceback.format_exc())

_main(egs=vars(Eg))
sys.exit(Eg.crash)
