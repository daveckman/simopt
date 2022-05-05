Model: <Traffic Control> (<trafficlight>)
==========================================

Description:
------------
<A model that simulates a series of intersections and their light schedules. As cars travel through the system, their waiting time is tracked.>

Sample math... :math:`S = 1500`

Sample math... 

.. math::
   \frac{ \sum_{t=0}^{N}f(t,k) }{N}
Sources of Randomness:
----------------------
<There are three sources of randomness in this model. All are created using the mrg32k3a random number generator.>

<The first two are modeled with uniform distributions and represent the start and end points of a car's path.>

* <Start and End Points>: <Random integer from 0 to the number of intersections>

<The third is modeled with an exponential distribution and represents the interarrival times of the cars.>

* <Interarrival Times>: <Exponentially distributed random variable with parameter lambda.>

Model Factors:
--------------
* <lambda>: <Float. Rate parameter of interarrival time distribution.>

    * Default: <0.5>

* <runtime>: <Float. Total time that the simulation runs.>

    * Default: <50>

* <numintersections>: <Int. Number of intersections.>

    * Default: <4>

* <interval>: <Float. Interval of time between light changes.>

    * Default: <5>    

* <offset>: <List. Delay in light schedule based on distance from first intersection.>

    * Default: <[0, 0, 0, 0]>

* <speed>: <Float. Constant that represents speed of cars when moving.>

    * Default: <2.5>  

* <distance>: <Float. Distance of travel between roads.>

    * Default: <5>

* <carlength>: <Float. Length of each car.>

    * Default: <1>  

* <reaction>: <Float. Reaction time of cars in queue.>

    * Default: <0.1>

Responses:
---------
* <WaitingTime>: <The average time a car sits in a queue.>


Optimization Problem: <Minimum Waiting Time in System> (<MinWaitingTime>)
========================================================

Decision Variables:
-------------------
* <offset>

Objectives:
-----------
<Minimize the average waiting time (<WaitingTime>) in system for the cars.>

Constraints:
------------
<All values in offset should be greater than 0.>

Problem Factors:
----------------
* <factor1name>: <short description>

  * Default: <default value>

* <factor2name>: <short description>

  * Default: <default value>

Fixed Model Factors:
--------------------
* <factor1name>: <fixed value>

* <factor2name>: <fixed value>

Starting Solution: 
------------------
* <dv1name>: <dv1initialvalue>

* <dv2name>: <dv2initialvalue>

Random Solutions: 
------------------
<description of how to generate random solutions>

Optimal Solution:
-----------------
<Unknowsn>

Optimal Objective Function Value:
---------------------------------
<Unknown>


...