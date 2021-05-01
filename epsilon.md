# Epsilon Reasonong

Call  the limits to reasoning _epsilon_ (&epsilon;). When two
solutions differ by less than &epsilon; then  they are indistinguishable.

&epsilon; is a useful early stopping  criteria.  When solutions are
indistinguishable then better solutions are unrecognizable (so you
might as  well stop).


When &epsilon; is large then many examples are actually repeats of
a smaller number of concepts. And when that is true, modeling and
control is simpler since there is less to model and control.

&espilon; is  everywhere:
- Sometimes our instrumentation
  is  only good at collecting data within  &plumn;&epsilon;. In that case, 
  there is no point exploring issues at &epsilon;/2.
- When processes only allow approximate control of parameters
  within some degree of &espilon;, then there  is  little point trying to propose
  solutions that are less that &epsilon; of the current  solution.
  For example,
  - If  car drivers can control
    the speed of  a car within &plusmn; 5s&nbsp; mph, then we should tell them
    "drive around 45&nbsp;mpg" rather than "drive at exactly "43&nbsp;mph:.
  - In many "human-oriented" control problems, you cannot ask people to change
    too much. So humans are "controllable" only within some &epsilon;.
- Some experimental methods repeat the same analysis, say, 20
  times 
  (each time using 90% of the data). This can generates 20 numbers that all
  differ by at least some value &epsilon;
- Epsilon can arrive from the mathematics  of sampling (see Discussion questions).

## Discussion

1. One common quick-and-dirty heuristic for saying two values are the same is _Cohen's rule_,
   i.e. Values that differ by less than 30% of the standard deviation are essentially
   the same 
   (standard deviation is a measure  of "wriggle" around the central tendency of
    a distribution: see [lib#sd](http://menzies.us/keys/lib.html#sd)):
   - Let &mu;=10 and &sigma.=5. Given Cohen's rule, what &epsilon; would you propose for this
   data.
   - For  many purposes, a normal Gaussian curve runs over &mu;&plumn;2&sigma;.  
     For those purposes, what does Cohen's rule say about the effective number of
     divisions $d$ of that data?
2. There are many  ways to calculate standard  deviation but my favorite is to
   sort all the numbers seen so far then divide the  90th percentile minus the 10th
   percentile by 2.56 
    - This method means that if we ever want to access (say) the 30th percentile, 
      we have access to all those numbers.
    - Also, this method makes no restrictive assumption that the data is symmetrical
      or normal.
   Using a [table of normal z-values](https://www.math.arizona.edu/~rsims/ma464/standardnormaltable.pdf),
   conform the above "2.56" values. (Hint:
   if 2.56 stretches 90th to 10th percentile then 2.56/2=1.28 is  half that; so see where
   1.28 falls in the table).
4. Calculating standard deviation via lists can  be slow (if large lists of numbers).
   To solve this,
   consider using a reservoir sampler that:
   - Keeps the  first  (say) `max=256` numbers,
   - After which time, new numbers replace old numbers in the reservoir at probability
   `max/n` (where `n` is the total number of  numbers  seen so far);
   - If ever a number is  kept, then set a flag `unordered=true`
   - If ever we want percentiles from this list, if `unordered`, we first  sort the list
     and  set `unordered=false`.

   Implement this reservoir sampler: 
   - Compute the standard deviation of a million  numbers _r()<sup>.5</sup>_ i
     (i.e. square root of a random number).
   - Starting at `max=10` and increasing by 50  to `max=500`, when do we start making
   mistakes about the standard deviation.
5. If the probability of success on one attempt is _p_, then the
   probability of failure on each attempt is _(1-p)_ and the probability
   of _n_ failures in a row is (1-p)<sup>n</sup>.  Hence, the
   probability of at least one success is     
   _s= 1–(1-p)<sup>n</sup>_. 
   - Solve this equation for _n_. Check your results at 
     _[Wolfram Alpha](https://www.wolframalpha.com)_
     using the query<br>
     _s=1-(1-p)^n,  0<p<1, 0<s<1,  solve for n_
   - As _s_ approaches 1, what happens to the number of tests _n_ for events
     occurring at a 1% probability? Try, for example, _s=0.90,0.95,0.99_ 
   - Recall your calculation of $d$ from Question1. How many samples do
     we need to be 95\% sure we can find a solution with probability 1/d?
   - A standard genetic algorithm makes 10<sup>4</sup> attempts to improve a solution
     (100 individuals mutated across 100 generations).  Given your _1/d_ Cohen result,
     what do you think of the need for 10<sup>4</sup> samples?
6. Cohen's rule, while simple, is often depreciated (since it makes naive parametric
   assumptions
   that the data is a symmetric curve with one single maximum point). An alternate
   method, that 
7. All the above seems to be  saying that learning can be successful from  a very
   small number of samples. What is the counter-case to all the above?
