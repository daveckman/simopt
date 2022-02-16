#!/usr/bin/env python
"""
Summary
-------
Provide dictionary directories listing solvers, problems, and models.

Listing
-------
solver_directory : dictionary
problem_directory : dictionary
model_directory : dictionary
"""
# import solvers
from solvers.astrodf import ASTRODF
from solvers.randomsearch import RandomSearch
# import models and problems
from models.cntnv import CntNV, CntNVMaxProfit
from models.mm1queue import MM1Queue, MM1MinMeanSojournTime
from models.facilitysizing import FacilitySize, FacilitySizingTotalCost, FacilitySizingMaxService
from models.rmitd import RMITD, RMITDMaxRevenue
from models.sscont import SSCont, SSContMinCost
from models.ironore import IronOre, IronOreMaxRev
from models.dynamnews import DynamNews, DynamNewsMaxProfit
from models.dualsourcing import DualSourcing, DualSourcingMinCost
from models.contam import Contamination, ContaminationTotalCostDisc, ContaminationTotalCostCont
from models.chessmm import ChessMatchmaking, ChessAvgDifference
from models.san import SAN, SANLongestPath
from models.hotel import Hotel, HotelRevenue
from models.tableallocation import TableAllocation, TableAllocationMaxRev
from models.paramesti import ParameterEstimation, ParamEstiMinLogLik
# directory dictionaries
solver_directory = {
    "ASTRODF": ASTRODF,
    "RNDSRCH": RandomSearch
}
problem_directory = {
    "CNTNEWS-1": CntNVMaxProfit,
    "MM1-1": MM1MinMeanSojournTime,
    "FACSIZE-1": FacilitySizingTotalCost,
    "FACSIZE-2": FacilitySizingMaxService,
    "RMITD-1": RMITDMaxRevenue,
    "SSCONT-1": SSContMinCost,
    "IRONORE-1": IronOreMaxRev,
    "DYNAMNEWS-1": DynamNewsMaxProfit,
    "DUALSOURCING-1": DualSourcingMinCost,
    "CONTAM-1": ContaminationTotalCostDisc,
    "CONTAM-2": ContaminationTotalCostCont,
    "CHESS-1": ChessAvgDifference,
    "SAN-1": SANLongestPath,
    "HOTEL-1": HotelRevenue,
    "TABLEALLOCATION-1": TableAllocationMaxRev,
    "PARAMESTI-1": ParamEstiMinLogLik
}
problem_nonabbreviated_directory = {
    "CntNVMaxProfit": CntNVMaxProfit,
    "MM1MinMeanSojournTime": MM1MinMeanSojournTime,
    "FacilitySizingTotalCost": FacilitySizingTotalCost,
    "FacilitySizingMaxService": FacilitySizingMaxService,
    "RMITDMaxRevenue": RMITDMaxRevenue,
    "SSContMinCost": SSContMinCost,
    "IronOreMaxRev": IronOreMaxRev,
    "DynamNewsMaxProfit": DynamNewsMaxProfit,
    "DualSourcingMinCost": DualSourcingMinCost,
    "ContaminationTotalCostDisc": ContaminationTotalCostDisc,
    "ContaminationTotalCostCont": ContaminationTotalCostCont,
    "ChessAvgDifference": ChessAvgDifference,
    "SANLongestPath": SANLongestPath,
    "HotelRevenue": HotelRevenue,
    "TableAllocationMaxRev": TableAllocationMaxRev,
    "ParamEstiMinLogLik": ParamEstiMinLogLik
}
model_directory = {
    "CNTNEWS": CntNV,
    "MM1": MM1Queue,
    "FACSIZE": FacilitySize,
    "RMITD": RMITD,
    "SSCONT": SSCont,
    "IRONORE": IronOre,
    "DYNAMNEWS": DynamNews,
    "DUALSOURCING": DualSourcing,
    "CONTAM": Contamination,
    "CHESS": ChessMatchmaking,
    "SAN": SAN,
    "HOTEL": Hotel,
    "TABLEALLOCATION": TableAllocation,
    "PARAMESTI": ParameterEstimation
}
model_unabbreviated_directory = {
    "CntNVMaxProfit": "CNTNEWS",
    "MM1MinMeanSojournTime": "MM1",
    "FacilitySizingTotalCost": "FACSIZE",
    "FacilitySizingMaxService": "FACSIZE",
    "RMITDMaxRevenue": "RMITD",
    "SSContMinCost": "SSCONT",
    "IronOreMaxRev": "IRONORE",
    "DynamNewsMaxProfit": "DYNAMNEWS",
    "DualSourcingMinCost": "DUALSOURCING",
    "ContaminationTotalCostDisc": "CONTAM",
    "ContaminationTotalCostCont": "CONTAM",
    "ChessAvgDifference": "CHESS",
    "SANLongestPath": "SAN",
    "HotelRevenue": "HOTEL",
    "TableAllocationMaxRev": "TABLEALLOCATION",
    "ParamEstiMinLogLik": "PARAMESTI"
}

