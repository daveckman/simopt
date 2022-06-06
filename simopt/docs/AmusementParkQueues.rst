Model: Amusement Park Queues (PARK-QUEUES)
==========================================

Description:
------------
This model simulates an amusement park with 7 attractions. Tourists arrive at
each attraction according to a poisson  distribution with a rate \[\gamma_i=1\]
i = 1,. . . , 7. Each attraction can only take one tourist at a time, while
others wait in a queue. The park has enough facilities to keep C tourists
waiting across all attractions. These facilities are to be distributed to
create queue capacities \[c_1]\,...,\[c7]\, such that \[\sum_{i=1}^{7} c_i = C\]
If a queue is full, the tourists will immediately leave the park.

After visiting each attraction, a tourist leaves the park with probability 0.2.
Otherwise, the tourist goes to another attraction according to the transition
matrix:

   1   2   3   4   5   6  7
1 0.1 0.1 0.1 0.1 0.2 0.2 0
2 0.1 0.1 0.1 0.1 0.2 0.2 0
3 0.1 0.1 0.1 0.1 0.2 0.2 0
4 0.1 0.1 0.1 0.1 0.2 0.2 0
5 0.1 0.1 0.1 0.1 0 0.1 0.3
6 0.1 0.1 0.1 0.1 0.1 0 0.3
7 0.1 0.1 0.1 0.1 0.1 0.1 0.2


The time that a tourist spend at an attraction follows an Erlang
distribution with shape parameter k = 2 and rate \[\lambda\] = 9. Without loss of
generality, suppose each attraction is occupied at all time. The park opens at
9AM and closes at 5PM, and the unit of time is minute. When the park closes,
all tourists in the queue leave immediately.

Sources of Randomness:
----------------------
There are 3 sources of randomness in this model:

* The arrival rate of tourists as a poisson distribution with rate of i=1,
i = 1, . . . , 7.

* The probability of 0.2 that a tourist leaves a park after visiting each
attraction and the associated probability matrix of their next attraction
otherwise.

* The time spent at each attraction as an Erlang distribution
with the shape parameter k = 2 and rate =9.



Model Factors:
--------------
* parkCapacity: The total number of tourists waiting for attractions that can
be maintained through park facilities, distributed across the attractions

    * Default: 350

* timeOpen: The number of minutes per day the park is open

    * Default: 480

* departProbability: The probability that a tourist will depart the park
after visiting an attraction

    * Default: 0.2

* queueCapacity1: The capacity of the queue for the first attraction based
on the portion of facilities allocated

    * Default: 50

* queueCapacity2: The capacity of the queue for the second attraction based
on the portion of facilities allocated

    * Default: 50

* queueCapacity3: The capacity of the queue for the third attraction based
on the portion of facilities allocated

    * Default: 50

* queueCapacity4: The capacity of the queue for the fourth attraction based
on the portion of facilities allocated

    * Default: 50

* queueCapacity5: The capacity of the queue for the fifth attraction based
on the portion of facilities allocated

    * Default: 50

* queueCapacity6: The capacity of the queue for the sixth attraction based
on the portion of facilities allocated

    * Default: 50

* queueCapacity7: The capacity of the queue for the seventh attraction based
on the portion of facilities allocated

    * Default: 50

number of attractions!!
//any parameter or setting of the model that someone could want to change//
//could be numerical or categorical//

Responses:
---------
* totalDepartedTourists: The total number of tourists to leave the park due
to full queues

* percentDepartedTourists: The percentage of tourists to leave the park due
to full queues


References:
===========
This model is adapted from the article:
Vill’en-Altamirano, J. (2009). Restart Simulation of Networks of Queues with
Erlang Service Times. Proceedings of the 2009 Winter Simulation Conference.




Optimization Problem: Minimize Total Departed Tourists (PARK-QUEUES-1)
========================================================

Decision Variables:
-------------------
* queueCapacity1
* queueCapacity2
* queueCapacity3
* queueCapacity4
* queueCapacity5
* queueCapacity6
* queueCapacity7


Objectives:
-----------
Minimize totalDepartedTourists

Constraints:
------------
* parkCapacity = 350

* i=17queueCapacityi=parkCapacity

* queueCapacity1 >= 0
* queueCapacity2 >= 0
* queueCapacity3 >= 0
* queueCapacity4 >= 0
* queueCapacity5 >= 0
* queueCapacity6 >= 0
* queueCapacity7 >= 0

Problem Factors:
----------------
* Budget: Max # of replications for a solver to take.

  * Default: 1000


Fixed Model Factors:
--------------------
* N/A

Starting Solution:
------------------
* dv1name: dv1initialvalue

* dv2name: dv2initialvalue

Random Solutions:
------------------
Generate a solution uniformly from a space of vectors of length 7 that sum up
350

Optimal Solution:
-----------------
unknown

Optimal Objective Function Value:
---------------------------------
unknown


Optimization Problem: <problem_name> (<problem_abbrev>)
========================================================

...
