# vim: ts=2 sw=2 sts=2 et :
import re

def csv(file, sep=",", dull=r'([\n\t\r ]|#.*)'):
  """Reads comma repeated files, one line  at a time, 
  deleting anything `dull`."""
  with open(file) as fp:
    for s in fp:
      s=re.sub(dull,"",s)
      if s:
        yield s.split(sep)

def first(a): 
  "First item" 
  return a[0]

class o:
  """Return a class can print itself (hiding "private" keys)
  and which can hold methods."""
  def __init__(i, **d)  : i.__dict__.update(d)
  def __repr__(i) : return "{"+ ', '.join( 
    [f":{k} {v}" for k, v in i.__dict__.items() if  k[0] != "_"])+"}"
