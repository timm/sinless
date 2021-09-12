# vim: ts=2 sw=2 sts=2 et :
import argparse
import about

def cli(usage, dict=about.CONFIG):
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
    if k0 in used: k0=k0.upper()
    c = used[k0] = k0  # (3)
    if default == False: # (2)
      add("-"+c, dest=k, default=False, help=help, action="store_true")
    else: # (1)
      add("-"+c, dest=k, default=default, help=help + " [" + str(default) + "]",
           type=type(default), metavar=k)
  return p.parse_args().__dict__
