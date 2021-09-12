from types import FunctionType as fun
import sys,traceback
from sinless import *
from cli import cli

class Eg:
  crash = 0
  def show(my): print(my)
  def works(my): assert True
  def fails(my): assert 1/0
  def _noop(my):  return 1
  def sym(my):
    s=Sym()
    for x in "aaaabb": s.add(x)
    print(s.has)
  def num(my):
    n=Num()
    for _ in range(10000): n.add(int(100*r()))
    print(n.all())
  def numDist(my):
    n=Num()
    for _ in range(10000): n.add(int(100*r()))
    print(n.dist("?",20))
  def data(my):
    d=Sample(my).load("weather.csv")
    print(d.x[1])
  def dist(my):
    d=Sample(my).load("auto93.csv")
    for row1 in d.rows:
      c,row2 = d.far(d.rows,row1)
      print("")
      print(row1.cells)
      print(row2.cells,int(100*c))
  def cluster(my):
    d=Sample(my).load("auto93.csv")
    d.cluster()

def _main(todo=Eg._noop, egs={}):
  """(1) Update the config using any command-line settings.
  (2) Maybe, udpate  `todo` from the  command line."""    
  my = o(**cli("python3 range.py [OPTIONS]"))
  if my.todo == "all":
    for k,f in egs.items():
      if type(f) == fun and k[0] != "_":
        _one(my, f)
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
