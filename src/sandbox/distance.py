# vim: ts=2 sw=2 sts=2 et :
import random

class Sym:
  def dist(i,x,y):
    "Distance: between two symbols"
    return 1 if x=="?" and y=="?" else (0 if x==y else 1)

class Num:
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

class Sample:
  def cluster(i):
    "Distance: Divide `d.rows` into a tree of  `depth`."
    out = []
    def div(rows, depth):
      if depth > i.my.depth  or len(rows) < i.my.end:
        out.append(i.clone(rows))
      else:
        left, right  = i.polarize(rows)
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
    rows = sorted([(i.dist(r1,r2),r2) for r2 in rows[:128]], 
                   key=lambda  z: z[0])
    return rows[int(i.my.far*len(rows))]

  def polarize(i,rows):
    "Distance: Separate rows via their distance to two distant points."
    anywhere = random.choice(rows)
    _,north  = i.faraway(rows, anywhere)
    c,south  = i.faraway(rows, north)
    for r in rows: 
      r.x = (i.dist(r,north)**2 + c**2 - i.dist(r,south)**2)/(2*c)
    rows  = sorted(rows, key=lambda row: row.x)
    mid   = len(rows)//2
    return rows[:mid], rows[mid:]


