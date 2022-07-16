Model: Network Queueing System Design (Network)
==========================================

Description:
------------
This model represents a communication system where is chosen routing percentages to route random arriving messages through a network. There are :math:`N` random messages that arrive following a Poisson process with a mean of :math:`lambda` that need to go to a particular destination and there are :math:`n` networks available to process these messages. The per message processing cost is :math:`c_1, c_2,..., c_n` depending on which network the message is routed through. It also takes time for a message to go through a network. This transit time is denoted by :math:`S_i` for each network :math:`i` and :math:`S_i` follows a triangular distribution with mean :math:`E(S_i)` and :math:`limits +- 0.5`. There is a cost for the length of time a message spends in a network measured by :math:`c` per each unit of time.
The decision variables are the routing percentages :math:`P_1,..., P_n E [0, 100]` which are the probabilities that a message will go through a particular network. When a message is in front of a network :math:`i` there is a :math:`P_i%` chance that it will be processed by network i, If the message packet is not processed by that network, then it will go to network :math:`i + 1`, and will be processed with probability :math:`P_i+1%` and so on. All messages arrive at network 1 with an exponentially distributed interarrival time with a mean of :math:`1/lambda`. The objective is to minimize total costs.

Sources of Randomness:
----------------------
    1. A message going through a particualr network.
    2. Interarrival time of a message. 
    3. The transit time for each network.

Model Factors:
--------------
* process_prob: Probability that a message will go through a particular network i 

    * Default: [10.0, 11.11111111111111, 12.5, 14.285714285714286, 16.666666666666668, 20, 25, 33.333333333333336, 50, 100]

* cost_process: Message processing cost of network i

    * Default: [1.0, 0.5, 0.3333333333333333, 0.25, 0.2, 0.16666666666666666, 0.14285714285714285, 0.125, 0.1111111111111111, 0.1]

* cost_time: Cost for the length of time a message spends in a network i per each unit of time

    * Default: 0.005
    
* mean_transit_time: Mean time of transit for network i following a triangular distribution 

    * Default: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
* limits_transit_time: Upper and lower limits for the triangular distribution for the transit time. 

    * Default: [[0.5,1.5], [1.5,2.5], [2.5,3.5], [3.5,4.5], [4.5,5.5], [5.5,6.5], [6.5,7.5], [7.5,8.5], [8.5,9.5], [9.5,10.5]]
    
* mean_arrival_time: Mean arrival rate of a message at network 1 for following a poission process

    * Default: 1
    
* n_messages: Number of messages that arrives and needs to be routed

    * Default: 1000

* n_networks: Number of networks

    * Default: 10
    
    
Responses:
---------
* total_cost: Total cost spent to route all messages


References:
===========
This model is adapted from the article "Queueing System Design" by Anjie Guo created on Julty 30, 2010 and updated by Jessica Wu. 



Optimization Problem: Minimize Total Cost (Network-1)
========================================================

Decision Variables:
-------------------
* process_prob

Objectives:
-----------
Let total_cost be the sum of the cost associated with length of a time spends in a network(cost_time) and the cost associated with processing a message(cost_process). 

Constraints:
------------
* :math:`0 <= P_1 < 100`
* :math:`0 <= P_(i-1) < 100     V i = [2, n]`
* :math:`P_n = 100` 

Problem Factors:
----------------
* initial_solution: Initial solution from which solvers start

  * Default: [10.0, 11.11111111111111, 12.5, 14.285714285714286, 16.666666666666668, 20, 25, 33.333333333333336, 50, 100]
  
* budget: Max # of replications for a solver to take.

  * Default: 10000

Fixed Model Factors:
--------------------
N/A

Starting Solution: 
------------------
* process_prob: [10.0, 11.11111111111111, 12.5, 14.285714285714286, 16.666666666666668, 20, 25, 33.333333333333336, 50, 100]


Random Solutions: 
------------------
Generate allocations uniformly at random from the set of vectors (of length equal to the number of networks) whose values are greater than one and less than 100 with the last probability of the vector being equal to 100.

Optimal Solution:
-----------------
Unkown

Optimal Objective Function Value:
---------------------------------
Unkown