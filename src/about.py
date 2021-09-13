# vim: ts=2 sw=2 sts=2 et :

CONFIG = dict( 
  bins = (float,.5,   "min bin size is n**bin"),
  cohen= (float,.35,  "ignore differences less than cohen*sd"),
  depth= (int,  5,    "dendogram depth"),
  end  = (int,  4,    "stopping criteria"),
  far  = (float,.9,   "where to find far samples"),
  loud = (bool, False,"loud mode: print stacktrace on error"),
  max  = (int,  500,  "max samples held  by `Nums`"),
  p    = (int,  2,    "co-efficient on distance equation"),
  seed = (int,  256,  "random number seed"),
  todo = (str,  "",   "todo: function (to be run at start-up)"),
  Todo = (str, False, "list available items for -t"))
