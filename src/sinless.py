#!/usr/bin/env python3
# vim: ts=2 sw=2 sts=2 et :
"""
This code tries to cure the following AI sins:
- AI tools, that require too much data, are hard to commission
- AI tools, that cannot explain themselves, do not permit transparency and accountability
- AI tools, that are needlessly complicated, waste CPU time and people time (and are hard to understand,
  test, and extend)
- AI tools, used off the shelf without tuning, are sub-optimal

To that end, we try:
- Use semi-supervised learning to reduce the commission costs (i.e. use fewer labels from the domain)
- Use symbolic AI tools that generate rules describing regions where concusions hold.
- Use epsilon domination to stop needlessly explore spurious details
- Use all the above in Hyperparameter optimizers so you can optimize the tool.

Does this solve all the problems of AI? Of course not.
But at least its a start. And as
St. Bernard of Clairvaux used to say:
"A saint is not someone who never sins, 
but one who sins less and less frequently and gets up more and more quickly"   

"""
import re, math, random
from lib import o,csv,first
r = random.random
 
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

  def discretize(i,j, my):
    "Query: `Return values seen in  i` is good and `j` is bad"
    best, rest = 1,0
    xys=[(good,best) for good in i._all] + [
         (bad, rest) for bad  in j._all]
    n1,n2 = len(i._all), len(j._all)
    iota = my.cohen * (i.var()*n1 + j.var()*n2) / (n1 + n2)
    ranges = merge(unsuper(xys, len(xys)**my.bins, iota))
    if len(ranges) > 1:
      for r in ranges:
        yield o(at=i.at, name=i.txt, lo=r.lo, hi=r.hi, 
                best= r.y.has.get(best,0), rest=r.y.has.get(rest,0))
       
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
    return 0  if abs(i.lo - i.hi) < 1E-31 else (x-i.lo) / (i.hi - i.lo)

  def per(i,p=.5,lo=None,hi=None):
    "Query: Return the item that is `p-th` beteeen `lo` and `hi`"
    a  = i.all()
    lo = lo or 0
    hi = hi or len(a)
    if hi==0: return "?"
    return a[int(lo + p*(hi - lo))]

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
    return (i.per(.9) - i.per(.1)) / 2.56

class Row(o):
  "Data: store rows"
  def __init__(i,lst,sample): 
     i.sample,i.cells, i.ranges = sample, lst,[None]*len(lst)

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
  def __init__(i,my, inits=[]): 
    "Creation"
    i.cols, i.rows, i.x, i.y, i.my = [],[],[],[], my
    [i.row(init) for init in inits]

  def __lt__(i,j):
    "Sort tables by their mid values."
    return  Row(i.mid(),i) < Row(j.mid(), j)

  def clone(i,inits=[]):
    "Copy: return a new sample with same structure as self"
    return Sample(i.my, 
                  inits=[[col.txt for col in i.cols]]+inits)

  def cluster(i):
    "Distance: Divide `d.rows` into a tree of  `depth`."
    out = []
    def div(rows, depth):
      if depth > i.my.depth  or len(rows) < i.my.end:
        leaf = i.clone(rows)
        print('|.. ' * depth, f"n={len(rows)}\t   goals={leaf.ys()}")
        out.append(leaf)
      else:
        left, right,c  = i.polarize(rows)
        print('|.. ' * depth, f"n={len(rows)} c={int(100*c)/100}")
        div(left,  depth + 1)
        div(right, depth + 1)
    div(i.rows, 1)
    return out

  def dist(i,r1,r2):
    "Distance: between two rows"
    d, n = 0, 1E-32
    for col in i.x:
      inc = col.dist( r1.cells[col.at], r2.cells[col.at] )
      d  += inc**i.my.p
      n  +=1
    return (d/n)**(1/i.my.p)

  def faraway(i, rows, r1):
    "Distance: to a remove row"
    random.shuffle(rows)
    rows = sorted([(i.dist(r1,r2),r2) for r2 in rows[:128]], key=first)
    return rows[int(i.my.far*len(rows))]

  def header(i,lst):
    "Creation: Create columns. Store dependent and independent columns in `x` and `y`"
    for c,x in enumerate(lst):
      what= Skip if "?" in x else (Num if x[0].isupper() else Sym)
      new = what(i.my,c,x)
      i.cols += [new]
      if "?" not in x:
        what = i.y if ("+" in x or "-" in x or "!" in x) else i.x
        what += [new]
 
  def load(i,file): 
    "Creation: Load data from a csv file in a Data instance."
    for lst in csv(file): i.row(lst)
    return i

  def mid(i):
    "Query: report middle"
    return [col.mid() for col in i.cols]

  def polarize(i,rows):
    "Distance: Separate rows via their distance to two distant points."
    anywhere = random.choice(rows)
    _,north  = i.faraway(rows, anywhere)
    c,south  = i.faraway(rows, north)
    for r in rows: 
      r.x = (i.dist(r,north)**2 + c**2 - i.dist(r,south)**2)/(2*c)
    rows  = sorted(rows, key=lambda row: row.x)
    mid   = len(rows)//2
    return rows[:mid], rows[mid:],c

  def row(i,lst):
    """Update: Turn `lst` into either a `header` (if it is row0) 
    or a `row` (for every other  line)."""
    lst = lst.cells if type(lst)==Row else lst
    if i.cols: i.rows += [Row([c.add(c.prep(x)) for c,x in zip(i.cols,lst)],i)]
    else: i.header(lst)

  def ys(i):
    "Query: report goals"
    return [col.mid() for col in i.y]

def unsuper(lst,big,iota):
  """Discretization: divide lst into bins of at least size 
  `big`, that span more than `iota`"""
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

def merge(b4):
  "Discretization: merge adjacent bins if they do not reduce the variability."
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

