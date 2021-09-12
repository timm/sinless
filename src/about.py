# vim: ts=2 sw=2 sts=2 et :

CONFIG = dict( 
  depth= (int,  5,    "dendogram depth"),
  end  = (int,  4,    "stopping criteria"),
  far  = (float,.9,   "where to find far samples"),
  max  = (int,  500,  "max samples held  by `Nums`"),
  p    = (int,  2,    "co-efficient on distance equation"),
  poorly = (int,  2,    "co-efficient on distance equation"),
  seed = (int,  256,  "random number seed"),
  todo = (str,  "",   "demo function (to be run at start-up)"),
  loud = (bool, False,"print stacktrace on error"))
