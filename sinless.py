#!/usr/bin/env python3
# vim: ts=2 sw=2 sts=2 et :
"""
Here are some AI sins, and their potential cure. If AI
generated models are too complex to understand, using symbolic
methods to find regions where conclusions hold. If the AI
need too much data, use semi-supervised learning to reduce
that commissioning cost. If the AI tools are needlessly
complicated, use epsilon domination to stop needlessly explore
spurious details. If the AI tools need tuning, use the above
to tune the models.
"""
from copy      import deepcopy as kopy
from types     import FunctionType as fun
from functools import wraps
import re, sys, math, random, argparse, traceback
r = random.random

CONFIG = dict(    
  bins = (float,.5,   "min bin size is n**bin"),    
  cohen= (float,.35,  "ignore differences less than cohen*sd"),    
  depth= (int,  5,    "dendogram depth"),     
  end  = (int,  4,    "stopping criteria"),    
  far  = (float,.9,   "where to find far samples"),      
  rule = (str,  "plan","assessment rule for a bin"),
  loud = (bool, False,"loud mode: print stacktrace on error"),    
  max  = (int,  500,  "max samples held  by `Nums`"),     
  p    = (int,  2,    "co-efficient on distance equation"),    
  seed = (int,  256,  "random number seed"),      
  todo = (str,  "",   "todo: function (to be run at start-up)"),     
  Todo = (str, False, "list available items for -t"),
  verbose=(str,False, "enable verbose prints")
)     

class o:
  "Return a class can print itself (hiding 'private' keys)"
  def __init__(i, **d)  : i.__dict__.update(d)
  def __getitem__(i, k) : return i.__dict__[k]
  def __repr__(i) : return "{"+ ', '.join(
    [f":{k} {v}" for k, v in i.__dict__.items() if  k[0] != "_"])+"}"

class Skip(o):
  "Column: Make something that ignores everything it sees."
  def __init__(i,_,n=0,s=""): i.n,i.at,i.txt,i.w = 0,n,s,1
  def add(i,x):  return  x
  def mid(i):    return "?"
  def prep(i,x): return x

class Sym(o):
  "Symbol counter."
  def __init__(i,my={},n=0,s=""): 
    "Creation"
    i.n,i.at,i.txt,i.has,i.w = 0,n,s,{},1
    i.mode, i.most = None,0

  def add(i,x,n=1): 
    "Update:  symbol counts."
    if x != "?": 
      i.n += n
      new = i.has[x] = n + i.has.get(x,0)
      if new > i.most:
         i.most,i.mmode = new, x
    return x

  def discretize(i,j,_):
    "Query: `Return values seen in  i` is good and `j` is bad"
    for x in set(i.has | j.has): 
      yield o(at=i.at, name=i.txt, lo=x, hi=x, 
              best= i.has.get(x,0), rest=j.has.get(x,0))

  def dist(i,x,y):
    "Distance: between two symbols"
    return 1 if x=="?" and y=="?" else (0 if x==y else 1)

  def merge(i,j):
    "Copy: merge two symbol counters"
    k = Sym(n=i.at, s=i.txt)
    for x,n in i.has.items(): k.add(x,n)
    for x,n in j.has.items(): k.add(x,n)
    return k

  def mid(i): 
    "Query: Central tendency"
    return i.mode

  def prep(i,x): 
    "Creation: Coerce `x` to a string."
    return x

  def var(i):
    "Query: variability"
    return - sum(v/i.n * math.log2(v/i.n) for v in i.has.values())

class Num(o):
  """Column: Numeric counters. This is a reservoir sampler;
   i.e. after a fixed number of items, new items replace older ones,
   selected at random."""
  def __init__(i, my=o(max=256), n=0, s=""):
    "Creation"
    i.n, i.at, i.txt, i._all =  0, n, s, []
    i.old, i.max, i.lo, i.hi = True, my.max, 1E32, -1E32  
    i.w= -1 if "-" in s else 1

  def add(i,x): 
    """Update: Keep a representative sample of the `x` values as
    well as the `lo` and `hi`  value  seen so far."""
    if x != "?":
      i.n += 1
      if x > i.hi: i.hi = x
      if x < i.lo: i.lo = x
      if len(i._all) < i.max: 
        i.old = True
        i._all += [x]
      elif r() < i.max/i.n: 
        i.old = True
        i._all[int(r()*len(i._all))] = x
    return  x

  def all(i):
    "Query: Return the stored numbers, sorted."
    if i.old: i._all.sort()
    i.old = False
    return i._all

  def discretize(columnFromHere, sameColumnFromThere, my):
    "Query: `Return values seen in  i` is good and `j` is bad"
    def unsuper(lst,big,iota):
      "make bins of size at least `big`, that span more than `iota`"
      lst  = sorted(lst, key=first)
      x= lst[0][0]
      now  = o(lo=x, hi=x, n=0, y=Sym())
      all  = [now]
      for i,(x,y) in enumerate(lst):
        if i < len(lst) - big:
          if now.n >= big:
             if now.hi - now.lo > iota:
               if x != lst[i+1][0]:
                 now = o(lo=x,hi=x,n=0,y=Sym())
                 all += [now]
        now.n += 1
        now.hi = x
        now.y.add(y)
      return all
    #--------------------------------
    def merge(b4):
      "merge adjacent bins if they do not reduce the variability."
      j,tmp = 0,[]
      while j < len(b4):
        a = b4[j]
        if j < len(b4) - 1:
          b = b4[j+1]
          cy = a.y.merge(b.y)
          if cy.var()*.95 <= (a.y.var()*a.n + b.y.var()*b.n)/(a.n + b.n):
             a = o(lo=a.lo, hi=b.hi, n=a.n+b.n, y=cy)
             j += 1
        tmp += [a]
        j += 1
      return merge(tmp) if len(tmp) < len(b4) else b4
    #--------------------------------
    i,j = columnFromHere, sameColumnFromThere
    best, rest = 1,0
    xys=[(good,best) for good in i._all] + [
         (bad, rest) for bad  in j._all]
    n1,n2 = len(i._all), len(j._all)
    iota = my.cohen * (i.var()*n1 + j.var()*n2) / (n1 + n2)
    bins = merge(unsuper(xys, len(xys)**my.bins, iota))
    if len(bins) > 1:
      for bin in bins:
        yield o(at=i.at, name=i.txt, lo=bin.lo, hi=bin.hi, 
                best= bin.y.has.get(best,0), 
                rest= bin.y.has.get(rest,0))

  def dist(i,x,y):
    "Distance: between two numbers."
    if x=="?" and y=="?": return 1
    if x=="?": 
      y = i.norm(y); x = 0 if y > 0.5 else 1
    elif y=="?": 
      x = i.norm(x); y = 0 if x > 0.5 else 1
    else:
      x,y = i.norm(x), i.norm(y)
    return abs(x - y)

  def mid(i):  
    "Query: mid point of the numbers."
    return i.per()

  def merge(i,j):
    "Copy: merge two numeric counters"
    k = Num(n=i.at, s=i.txt)
    for x in i._all: k.add(x)
    for x in j._all: k.add(x)
    return k

  def norm(i,x): 
    "Query: return 0..1"
    return 0 if abs(i.hi - i.lo) < 1E-31 else (x-i.lo) / (i.hi - i.lo)

  def per(i,p=.5,lo=None,hi=None):
    "Query: Return the item that is `p-th` beteeen `lo` and `hi`"
    a  = i.all()
    lo = lo or 0
    hi = hi or len(a)
    return "?" if hi==0 else a[int(lo + p*(hi - lo))]

  def prep(i,x): 
    "Creation: Coerce `x` to a float."
    return x if x=="?" else float(x)

  def var(i): 
    """<img align=right width=300 
    src="https://miro.medium.com/max/1400/1*IZ2II2HYKeoMrdLU5jW6Dw.png">
    Query: variability.
    As well know,  plus or minus (1,2) sd is (66%,95%) of the area 
    under the normal curve.  Another number of interest is that  plus or 
    minus 1.28 sd is 90% of the mass.  This means that one standard 
    deviation is 90% of the mass divided by (1.28*2)=2.56. Hence,
    to compute something analogous to sd from any distribution, 
    sort it and look at the 90th and 10th percentile. <br clear=all>"""
    return (i.per(.9) - i.per(.1)) / 2.56 if len(i._all) < 2  else 0

class Row(o):
  "Data: store rows"
  def __init__(i,lst,sample): 
     i.sample,i.cells, = sample, lst

  def __lt__(i,j):
    "Does row1 win over row2?"
    s1, s2, n = 0, 0, len(i.sample.y)
    for col in i.sample.y:
      a   = col.norm(i.cells[col.at])
      b   = col.norm(j.cells[col.at])
      s1 -= math.e**(col.w * (a - b) / n)
      s2 -= math.e**(col.w * (b - a) / n)
    return s1 / n < s2 / n

  def ys(i):
    "Query: the goal values of this row"
    return [i.cells[col.at] for col in i.sample.y]

class Sample(o):
  "Data: store rows and columns"
  def __init__(i,my, inits=[], keep=True): 
    "Creation"
    i.cols, i.rows, i.x, i.y, i.my = [],[],[],[], my
    i.keep = keep
    [i.add(init) for init in inits]

  def __lt__(i,j):
    "Sort tables by their mid values."
    return  Row(i.mid(),i) < Row(j.mid(), j)

  def add(i,lst):
    """Update: Turn `lst` into either a `header` (if it is row0) 
    or a `row` (for every other  line)."""
    lst = lst.cells if type(lst)==Row else lst
    if i.cols: 
      row = [c.add(c.prep(x)) for c,x in zip(i.cols,lst)]
      if i.keep:
        i.rows += [Row(row,i)]
    else:  # this is top row and we need to fill in `i.cols`
      for c,x in enumerate(lst):
        what = Skip if "?" in x else (Num  if x[0].isupper() else Sym)
        new  = what(i.my,c,x)
        i.cols += [new]
        if "?" not in x: 
          (i.y if ("+" in x or "-" in x or "!" in x) else i.x).append(new)

  def clone(i,inits=[]):
    "Copy: return a new sample with same structure as self"
    return Sample(i.my, inits=[[col.txt for col in i.cols]] + inits)

  def cluster(i, rows=None):
    "Distance: Divide `d.rows` into a tree of  `depth`."
    def polarizing(rows, depth=1):
      "Cluster via recursive polarizing the data."
      if i.my.verbose:
        print('|.. '*(depth-1) + str(len(rows)))
      if depth > i.my.depth  or len(rows) < i.my.end:
        out.append(i.clone(rows))
      else:
        left, right = i.polarize(rows)
        polarizing(left,  depth + 1)
        polarizing(right, depth + 1)
    #-------------------------------
    out = []
    polarizing(rows or i.rows)
    return out

  def dist(i,r1,r2):
    "Distance: between two rows"
    d, n = 0, 1E-32
    for col in i.x:
      inc = col.dist( r1.cells[col.at], r2.cells[col.at] )
      d  += inc**i.my.p
      n  +=1
    return (d/n)**(1/i.my.p)

  def load(i,file): 
    "Creation: Load data from a csv file in a Data instance."
    for lst in csv(file): i.add(lst)
    return i

  def mid(i):
    "Query: report middle"
    return [col.mid() for col in i.cols]

  def polarize(i,rows=None):
    "Return rows seperated by two far points."
    def far(r1,rows):
      "From `n` random rows, return the `i.my.far*n`-th row from `r1`"
      n = min(128,len(rows))
      return sorted([(i.dist(r1,r2),r2) 
        for r2 in random.sample(rows,n)], key=first)[int(i.my.far*n)]
    rows     = rows or i.rows
    anywhere = random.choice(rows)
    _,north  = far(anywhere,rows)
    c,south  = far(north,rows)
    cosine   = lambda a,b,c: (a**2 + c**2 - b**2)/(2*c)
    for r in rows: 
      r.x = cosine(i.dist(r,north), i.dist(r,south), c)  
    rows  = sorted(rows, key=lambda row: row.x)
    mid   = len(rows)//2
    return rows[:mid], rows[mid:]

  def ys(i):
    "Query: report goals"
    return [col.mid() for col in i.y]

def value(rule, bin, bests, rests):
  funs = o(plan    = lambda b,r: b**2/(b+r) if b>r else 0,
           monitor = lambda b,r: r**2/(b+r) if r>b else 0,
           novel   = lambda b,r: 1/(b+r))
  return funs[rule](bin.best/bests, bin.rest/rests)

# XXXX test
def fft(s,my):
  def ordered(rule,like,hate):
    return  sorted([(value(rule,bin,like.n,hate.n), bin) for b in bins],
                     reverse=True, key=first)[1]

  best, rest = sorted([s.clone(rows) for rows in s.polarize()])
  bins = [bin for like,hate in zip(best.x, rest.x) 
              for bin in like.discretize(hate,my)]
  plan  = ordered("plan",best,rest)
  monitor  = ordered("monitor",best,rest)
  print(plan)
  print(monitor)

def csv(file, sep=",", dull=r'([\n\t\r ]|#.*)'):
  "Yield lines from comma repeated files, deleting `dull` things."
  with open(file) as fp:
    for s in fp:
      s=re.sub(dull,"",s)
      if s: yield s.split(sep)

def first(a): 
  "First item" 
  return a[0]

class Eg:
  all, crash = {}, -1

  def one(f): 
    "Define one example."
    if f.__name__[0] != "_": Eg.all[f.__name__] = f
    return f

  def cli(usage,dict):
    """
    (1) Execute a command-line parse that uses `dict` keys as  command line  flags
        (so expect `dict` values to be tuples (type, defaultValue,help));   
    (2) Define switches for  defaults that re `False`;    
    (3) If keys repeat, make the  second one upper case."""
    p    = argparse.ArgumentParser(prog=usage, description=__doc__, 
                      formatter_class=argparse.RawTextHelpFormatter)
    add  = p.add_argument
    used = {}
    for k, (ako, default, help) in sorted(dict.items()):
      k0 = k[0]
      k0 = k0.upper() if k0 in used else k0
      c = used[k0] = k0  # (3)
      if default == False: # (2)
        add("-"+c, dest=k, default=False, 
            help=help, action="store_true")
      else: # (1)
        add("-"+c, dest=k, default=default, 
            help=help + " [" + str(default) + "]",
            type=type(default), metavar=k)
    return p.parse_args().__dict__

  def run1(my, f):
    """Set seed to a common standard. 
    Run. Increment crash if crash."""
    random.seed(my.seed)
    try: 
      f(my)
      print(f"\x1b[1;32m✔ {f.__name__}\x1b[0m")
    except Exception as err:
      Eg.crash += 1
      print(f"\x1b[1;31m✘  {f.__name__}\x1b[0m")
      if my.loud: print(traceback.format_exc())
  
  def run():
    """(1) Update the config using any command-line settings.
       (2) Maybe, update `todo` from the  command line."""    
    my = o(**Eg.cli("python3.9 eg.py [OPTIONS]",CONFIG))
    if my.Todo: 
      return [print(f"{name:>15} : {f.__doc__ or ''}") 
              for name,f in Eg.all.items()]
    if my.todo == "all":
      for _,f in Eg.all.items():
        my = kopy(my)
        Eg.run1(my,f)
      print("Errors:", Eg.crash)
      sys.exit(Eg.crash)
    else:
      if my.todo:
        Eg.run1(my, Eg.all[my.todo])
