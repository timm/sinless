#!/usr/bin/env python3
# vim: ts=2 sw=2 sts=2 et :
"""
Cluster  + Contrast
"""
import re, random
from lib import o,csv,first
r = random.random
  
class Skip(o):
  "Make something that ignores everything it sees."
  def __init__(i,_,n=0,s=""): i.n,i.at,i.txt = 0,n,s
  def add(i,x):  return  x
  def prep(i,x): return x

class Sym(o):
  "Symbol counter."
  def __init__(i,my={},n=0,s=""): i.n,i.at,i.txt,i.has = 0,n,s,{}

  def add(i,x): 
    "Update symbol counts."
    if x != "?": 
      i.n += 1
      i.has[x] = 1 + i.has.get(x,0)
    return x

  def dist(i,x,y):
    "Distance between two symbols"
    return 1 if x=="?" and y=="?" else (0 if x==y else 1)

  def prep(i,x): 
    "Coerce `x` to a string."
    return x


class Num(o):
  "Numeric counters."
  def __init__(i, my=o(max=256), n=0, s=""):
    i.n, i.at, i.txt, i._all =  0, n, s, []
    i.old, i.max, i.lo, i.hi = True, my.max, 1E32, -1E32  
    i.w= -1 if "-" in s else 1

  def add(i,x): 
    """Keep a representative sample of the `x` values as
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
    "Return the stored numbers, sorted."
    if i.old: i._all.sort()
    i.old = False
    return i._all

  def dist(i,x,y):
    "Distance between two numbers."
    def norm(z): return (z-i.lo) / (i.hi - i.lo +1E-31)
    if x=="?" and y=="?": return 1
    if x=="?": 
      y = norm(y); x = 0 if y > 0.5 else 1
    elif y=="?": 
      x = norm(x); y = 0 if x > 0.5 else 1
    else:
      x,y = norm(x), norm(y)
    return abs(x - y)

  def mid(i):  
    "Return  the mid point of the numbers."
    return i.per()

  def per(i,p=.5,lo=None,hi=None):
    "Return the item that is `p-th` beteeen `lo` and `hi`"
    a  = i.all()
    lo = lo or 0
    hi = hi or len(a)
    return a[int(lo + p*(hi - lo))]

  def prep(i,x): 
    "Coerce `x` to a float."
    return x if x=="?" else float(x)

  def sd(i): 
    """<img align=right width=300 
        src="https://miro.medium.com/max/1400/1*IZ2II2HYKeoMrdLU5jW6Dw.png">
    - Plus or minus (1,2) sd is (66%,95%) of the mass. 
    - So plus or minus 1.28 is 90% of the mass. 
    - So one standard deviation is 90% of the mass divided by 2.56.<br clear=all>"""
    return (i.per(.9) - i.per(.1)) / 2.56

class Row(o):
  def __init__(i,lst): i.cells, i.ranges = lst,[None]*len(lst)

class Data(o):
  def __init__(i,my): 
    i.cols, i.rows, i.x, i.y = [],[],[],[]
    i.my = my

  def load(i,file): 
    "Load data from a csv file in a Data instance."
    for lst in csv(file): i.row(lst)
    return i

  def row(i,lst):
    """Turn `lst` into either a `header` (if it is row0) 
    or a `row` (for every other  line)."""
    if i.cols: i.rows += [Row([c.add(c.prep(x)) for c,x in zip(i.cols,lst)])]
    else: i.header(lst)

  def header(i,lst):
    "Create columns. Store dependent and independent columns in `x` and `y`"
    for c,x in enumerate(lst):
      what= Skip if "?" in x else (Num if x[0].isupper() else Sym)
      new = what(i.my,c,x)
      i.cols += [new]
      if "?" not in x:
        what = i.y if ("+" in x or "-" in x or "!" in x) else i.x
        what += [new]

  def dist(i,r1,r2):
    d, n = 0, 1E-32
    for col in i.x:
      inc = col.dist( r1.cells[col.at], r2.cells[col.at] )
      d  += inc**i.my.p
      n  +=1
    return (d/n)**(1/i.my.p)

  def far(i, rows, r1):
    random.shuffle(rows)
    rows = sorted([(i.dist(r1,r2),r2) for r2 in rows[:128]], key=first)
    return rows[int(i.my.far*len(rows))]
 
  """
  ---------------
  asdad
  """
  def polarize(i,rows,d):
    "Separate rows via their distance to two distant points."
    anywhere = random.choice(rows)
    _,north  = i.far(rows, anywhere)
    c,south  = i.far(rows, north)
    for r in rows: 
      r.x = (i.dist(r,north)**2 + c**2 - i.dist(r,south)**2)/(2*c)
    rows  = sorted(rows, key=lambda row: row.x)
    mid   = len(rows)//2
    return rows[:mid], rows[mid:]

  def cluster(i):
    "Divide `d.rows` into a tree of  `depth`."
    out = []
    def div(rows, depth):
      if depth > i.my.depth  or len(rows) < i.my.end:
        out.append(Cluster(rows))
      else:
        left, right  = i.polarize(rows,depth)
        div(left,  depth + 1)
        div(right, depth + 1)
    div(i.rows, 1)
    return out

class Cluster(o):
  def __init__(i,has): i.has = has

# def ranges(d):     
#   for c in d.x:
#     if d.cols[c] == num: 
#       lst        = [(row[c],row) for row in d.rows if row[c] != "?"]
#       d.ranges[c]= [closer(d,n,range1) for n,range1 in 
#                     enumerate(ranges1(lst,col=col))]
#
# def ranges1(lst,col=0):
#   "Break list  "
#   lst     = sorted(lst, key=first)
#   iota    = sd(lst, key=first) * .35
#   big     = int( max(len(lst)/16, len(lst)**.5))
#   lo      = x[0][0]
#   range1  = o(col=col, lo=lo, hi=lo, has=[])
#   out    += [range1]
#   for i,(x,row) in enumerate(lst):
#     if i < len(lst) - big:
#       if len(range1.has) >= big:
#          if range1.hi - range1.low > iota:
#            if x != lst[i+1][0]:
#              range1 = o(col=col, lo=x, hi=x, has=[])
#              out += [range1]
#     range1.hi   = x 
#     range1.has += [row]
#   return out
#
# def dist(d, row1,row2):
#    i1,i2 = id(row1), id(row2)
#    if i1 > i2: i1,i2 = i2,i1
#    if i1 in d.close:
#      if i2 in d.close[i2]:
#        return 1 - d.close[i1][i2] / d.closest
#    return 1 

