Model: <model_name> (<model_abbreviation>)
==========================================

Description:
------------
A communication system routes messages that need to go their respective destinations that goes through a network and has an associated cost. This model simulates a network system that routes different messages through the system to try to minimize the total cost.

There are different probabilities and routing percentages that will be represented by P1, P2,... and so on. There is an associated cost per message  that is dependent on the amount of time the message was in the network that will be represented by c1,c2,... and so on.

Sample math... :math:`S = 1500`

Sample math... 

.. math::

   \frac{ \sum_{t=0}^{N}f(t,k) }{N}

Sources of Randomness:
----------------------
1. A stationary Poisson proccess with rate 1/lambda for message arrivals.
Model Factors:
--------------
* i: The measurement of time 

   * Default: minutes
   
* timecost: The cost of having a message in the network.

    * Default: $1 for each i
    
* c: Processing cost of each message

   * Default: $.005

* N: Number of random messages that arrive

    * Default: 1000

* n: Numer of networks available to process messages

    * Default: 10
    
*Pi: Probability for network i for each i

Responses:
---------
* optimized_pi: most efficient probability of entering network i 


References:
===========
Barton, R. R., & Meckesheimer, M. (2006). Metamodel-Based Simulation Optimization.
S.G. Henderson and B.L. Nelson (Eds.), Handbook in OR & MS, Vol. 13




Optimization Problem: <problem_name> (<problem_abbrev>)
========================================================

Decision Variables:
-------------------
* Pi for each i

Objectives:
-----------
Minimize total costs of the network system.

Constraints:
------------
* Cannot have negative costs
* Cannot have negative number of messages arrive

Problem Factors:
----------------
* working_time: amount of time the network is up and running

  * Default: 24 hrs
  

Fixed Model Factors:
--------------------
* N/A

Starting Solution: 
------------------
* original_soln: Pi = 100/(n-i+1) for each i

Random Solutions: 
------------------
???

Optimal Solution:
-----------------
Unknown

Optimal Objective Function Value:
---------------------------------
Unknown

Optimization Problem: <problem_name> (<problem_abbrev>)
========================================================

...
