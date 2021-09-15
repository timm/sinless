# vim: ts=2 sw=2 sts=2 et :
"""
Traits for  discretiztion
"""

class Sym:
  def discretize(i,j,_):
    "Query: `Return values seen in  i` is good and `j` is bad"
    for x in set(i.has | j.has): 
      yield o(at=i.at, name=i.txt, lo=x, hi=x, 
                best= i.has.get(x,0), rest=j.has.get(x,0))


class Num:
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

