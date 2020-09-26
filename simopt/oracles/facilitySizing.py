# Multi variate normal distribution

import numpy as np
import random
import sys

mean_demand_arr = np.array([10, 230, 221]).reshape(3, 1)
cov_mat = np.array([[2276, 1508, 813], [1508, 2206, 1349], [813, 1349, 1865]])

# Check is cov matrix is positive definite
def check_positive_definite(cov_mat):
    cov_eigen_mat = np.linalg.eigvals(cov_mat)
    return all(i>=0 for i in cov_eigen_mat)

if check_positive_definite(cov_mat) == False:
    print("Covariance matrix isnt positive definite")
    sys.exit()

# Generate trucated multivariate normal distribution
flag_truncated_normal = False

# Get cholesky decomposition
cholesky_decomposition_mat = np.linalg.cholesky(cov_mat)

# Check to see if chol_mat*chol_mat_transpose = Cov_mat
# print(cholesky_decomposition_mat)
# print(np.dot(cholesky_decomposition_mat, np.transpose(cholesky_decomposition_mat)))

number_of_items = mean_demand_arr.shape[0]
while flag_truncated_normal == False:

    # Generate standard normal samples
    sample_demand = np.random.normal(loc=0, scale=1, size=number_of_items).reshape(number_of_items, 1)
    multivariate_normal_demand_sample = mean_demand_arr + np.dot(cholesky_decomposition_mat, sample_demand)
    multivariate_normal_demand_sample = multivariate_normal_demand_sample.reshape(-1)

    # Check if all items are positive
    flag_truncated_normal = all(i>=0 for i in multivariate_normal_demand_sample)
    print(multivariate_normal_demand_sample)



















# """
# Summary
# -------
# Simulate a period worth of demand to compare against facility capacity
# """
# from base import Oracle
# import numpy as np

# class FacilitySizing(Oracle):
#     """
#     An oracle that simulates a demand and compares with the capacity of the facility
#     Attributes
#     ----------
#     n_rngs : int
#         number of random-number generators used to run a simulation replication
#     rng_list : list of rng.MRG32k3a objects
#         list of random-number generators used to run a simulation replication
#     n_responses : int
#         number of responses (performance measures)
#     factors : dict
#         changeable factors of the simulation model
#     specifications : dict
#         details of each factor (for GUI, data validation, and defaults)
#     check_factor_list : dict
#         switch case for checking factor simulatability
#     Arguments
#     ---------
#     fixed_factors : dict
#         fixed_factors of the simulation model
#     See also
#     --------
#     base.Oracle
#     """
#     def __init__(self, fixed_factors={}):
#         self.n_rngs = 1
#         self.n_responses = 1
#         self.factors = fixed_factors
#         self.specifications = {
#             "facility_size": {
#                 "description": "Capacity of the facility",
#                 "datatype": float,
#                 "default": 5.0
#             },
#             "facility_cost": {
#                 "description": "Unit cost of installing the facility",
#                 "datatype": float,
#                 "default": 9.0
#             },
#             "risk_level": {
#                 "description": "Target Service level", # Need help here
#                 "datatype": float,
#                 "default": 1.0
#             },
#             "number_of_products": {
#                 "description": "number of products stored at the facility",
#                 "datatype": float,
#                 "default": 20.0
#             }, 
#             "mean_demand":{
#                 "description": "Array of Expected demand values for each product",
#                 "datatype": float, # or int
#                 "default": 0.5
#             },
#             "stdev_demand": {
#                 "description": "Standard deviation of demand for each product",
#                 "datatype": float,
#                 "default": 2.0
#             },
            
#         }
#         self.check_factor_list = {
#             "purchase_price": self.check_facility_size,
#             "sales_price": self.check_facility_cost,
#             "salvage_price": self.check_salvage_price,
#             "order_quantity": self.check_order_quantity,
#             "Burr_c": self.check_Burr_c,
#             "Burr_k": self.check_Burr_k
#         }
#         # set factors of the simulation oracle
#         super().__init__(fixed_factors)

#     # Check for simulatable factors
#     def check_facility_size(self):
#         return self.factors["facility_size"] > 0

#     def check_facility_cost(self):
#         return self.factors["facility_cost"] > 0

#     def check_risk_level(self):
#         return self.factors["risk_level"] > 0 and self.factors["risk_level"] <1

#     def check_order_quantity(self):
#         return self.factors["order_quantity"] > 0

#     def check_Burr_c(self):
#         return self.factors["Burr_c"] > 0

#     def check_Burr_k(self):
#         return self.factors["Burr_k"] > 0

#     def check_simulatable_factors(self):
#         return self.factors["salvage_price"] < self.factors["purchase_price"] < self.factors["sales_price"]

#     def replicate(self):
#         """
#         Simulate a single replication for the current oracle factors.
#         Returns
#         -------
#         responses : dict
#             performance measures of interest
#             "profit" = profit in this scenario
#         """
#         # designate random number generator
#         demand_rng = self.rng_list[0]
#         # generate Burr Type XII random demand
#         demand = ((1-demand_rng.random())**(-1/self.factors["Burr_k"])-1)**(1/self.factors["Burr_c"])
#         # calculate profit 
#         profit = -1*self.factors["purchase_price"]*self.factors["order_quantity"] + min(demand, self.factors["order_quantity"])*self.factors["sales_price"] + max(0, self.factors["order_quantity"]-demand)*self.factors["salvage_price"]
#         # calculate gradient of profit w.r.t. order quantity
#         if demand > self.factors["order_quantity"]:
#             grad_profit_order_quantity = self.factors["sales_price"] - self.factors["purchase_price"]
#         elif demand < self.factors["order_quantity"]:
#             grad_profit_order_quantity = self.factors["salvage_price"] - self.factors["purchase_price"]
#         else:
#             grad_profit_order_quantity = np.nan
#         # compose responses
#         responses = {"profit": profit}
#         # compose gradients
#         gradients = {response_key: {factor_key: np.nan for factor_key in self.specifications} for response_key in responses}
#         gradients["profit"]["order_quantity"] = grad_profit_order_quantity
#         # return responses and gradients
#         return responses, gradients