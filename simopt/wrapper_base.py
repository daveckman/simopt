#!/usr/bin/env python
"""
Summary
-------
Provide base classes for experiments and meta experiments.
Plus helper functions for reading/writing data and plotting.

Listing
-------
Experiment : class
record_experiment_results : function
read_experiment_results : function
stylize_plot : function
stylize_solvability_plot : function
save_plot : function
area_under_prog_curve : function
solve_time_of_prog_curve : function
MetaExperiment : class
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import pickle
import importlib

from rng.mrg32k3a import MRG32k3a
from base import Solution
from directory import solver_directory, problem_directory


class Experiment(object):
    """
    Base class for running one solver on one problem.

    Attributes
    ----------
    solver : base.Solver object
        simulation-optimization solver
    problem : base.Problem object
        simulation-optimization problem
    n_macroreps : int > 0
        number of macroreplications run
    all_recommended_xs : list of lists of tuples
        sequences of recommended solutions from each macroreplication
    all_intermediate_budgets : list of lists
        sequences of intermediate budgets from each macroreplication
    all_reevaluated_solns : list of Solution objects
        reevaluated solutions recommended by the solver
    all_post_replicates : list of lists of lists
        all post-replicates from all solutions from all macroreplications
    all_est_objective : numpy array of arrays
        estimated objective values of all solutions from all macroreplications
    all_prog_curves : numpy array of arrays
        estimated progress curves from all macroreplications
    initial_soln : base.Solution object
        initial solution (w/ postreplicates) used for normalization
    ref_opt_soln : base.Solution object
        reference optimal solution (w/ postreplicates) used for normalization
    areas : list of floats
        areas under each estimated progress curve
    area_mean : float
        sample mean area under estimated progress curves
    area_std_dev : float
        sample standard deviation of area under estimated progress curves
    area_mean_CI : numpy array of length 2
        bootstrap CI of the form [lower bound, upper bound] for mean area
    area_std_dev_CI : numpy array of length 2
        bootstrap CI of the form [lower_bound, upper_bound] for std dev of area
    solve_tol : float in (0,1]
        relative optimality gap definining when a problem is solved
    solve_times = list of floats
        solve_tol solve times for each estimated progress curve
    solve_time_quantile : float
        beta quantile of solve times
    solve_time_quantile_CI : numpy array of length 2
        bootstrap CI of the form [lower bound, upper bound] for quantile of solve time

    Arguments
    ---------
    solver_name : string
        name of solver
    problem_name : string
        name of problem
    solver_fixed_factors : dict
        dictionary of user-specified solver factors
    problem_fixed_factors : dict
        dictionary of user-specified problem factors
    oracle_fixed_factors : dict
        dictionary of user-specified oracle factors
    """
    def __init__(self, solver_name, problem_name, solver_fixed_factors={}, problem_fixed_factors={}, oracle_fixed_factors={}):
        # TO DO: problem_fixed_factors is not used yet
        self.solver = solver_directory[solver_name](fixed_factors=solver_fixed_factors)
        self.problem = problem_directory[problem_name](oracle_fixed_factors=oracle_fixed_factors)
        self.all_recommended_xs = []
        self.all_intermediate_budgets = []
        self.all_reevaluated_solns = []

    def run(self, n_macroreps, crn_across_solns):
        """
        Run n_macroreps of the solver on the problem.

        Arguments
        ---------
        n_macroreps : int
            number of macroreplications of the solver to run on the problem
        crn_across_solns : bool
            indicates if CRN are used when simulating different solutions
        """
        self.n_macroreps = n_macroreps
        # Create, initialize, and attach random number generators
        #     Stream 0: reserved for taking post-replications
        #     Stream 1: reserved for bootstrapping
        #     Stream 2: reserved for overhead ...
        #         Substream 0: rng for random problem instance
        #         Substream 1: rng for random initial solution x0 and
        #                      restart solutions
        #         Substream 2: rng for selecting random feasible solutions
        #         Substream 3: rng for solver's internal randomness
        #     Streams 3, 4, ..., n_macroreps + 2: reserved for
        #                                         macroreplications
        rng0 = MRG32k3a(s_ss_sss_index=[2, 0, 0])  # unused
        rng1 = MRG32k3a(s_ss_sss_index=[2, 1, 0])  # unused
        self.solver.attach_rngs([MRG32k3a(s_ss_sss_index=[2, 2, 0])])
        rng3 = MRG32k3a(s_ss_sss_index=[2, 3, 0])  # unused
        # Run n_macroreps of the solver on the problem.
        # Report recommended solutions and corresponding intermediate budgets.
        for mrep in range(self.n_macroreps):
            # Create, initialize, and attach RNGs for oracle.
            oracle_rngs = [MRG32k3a(s_ss_sss_index=[mrep + 2, ss, 0]) for ss in range(self.problem.oracle.n_rngs)]
            self.problem.oracle.attach_rngs(oracle_rngs)
            # Run the solver on the problem.
            recommended_solns, intermediate_budgets = self.solver.solve(problem=self.problem, crn_across_solns=crn_across_solns)
            # Extract decision-variable vectors (x) from recommended solutions.
            # Record recommended solutions and intermediate budgets.
            self.all_recommended_xs.append([solution.x for solution in recommended_solns])
            self.all_intermediate_budgets.append(intermediate_budgets)
        # Save Experiment object to .pickle file.
        file_name = self.solver.name + "_on_" + self.problem.name
        record_experiment_results(experiment=self, file_name=file_name)


    def post_replicate(self, n_postreps, n_postreps_init_opt, crn_across_budget=True, crn_across_macroreps=False):
        """
        Run postreplications at solutions recommended by the solver.

        Arguments
        ---------
        n_postreps : int
            number of postreplications to take at each recommended solution
        n_postreps_init_opt : int
            number of postreplications to take at initial x0 and optimal x*
        crn_across_budget : bool
            use CRN for post-replications at solutions recommended at different times?
        crn_across_macroreps : bool
            use CRN for post-replications at solutions recommended on different macroreplications?
        """
        self.n_postreps = n_postreps
        self.n_postreps_init_opt = n_postreps_init_opt
        # Create, initialize, and attach RNGs for oracle.
        # Stream 0: reserved for post-replications.
        oracle_rngs = [MRG32k3a(s_ss_sss_index=[0, rng_index, 0]) for rng_index in range(self.problem.oracle.n_rngs)]
        self.problem.oracle.attach_rngs(oracle_rngs)
        # Simulate common initial solution x0.
        x0 = self.problem.initial_solution
        self.initial_soln = Solution(x0, self.problem)
        self.problem.simulate(solution=self.initial_soln, m=self.n_postreps_init_opt)
        if crn_across_budget is True:
            # Reset each rng to start of its current substream.
            for rng in self.problem.oracle.rng_list:
                rng.reset_substream()
        # Simulate "reference" optimal solution x*.
        xstar = self.problem.ref_optimal_solution
        self.ref_opt_soln = Solution(xstar, self.problem)
        self.problem.simulate(solution=self.ref_opt_soln, m=self.n_postreps_init_opt)
        if crn_across_budget is True:
            # Reset each rng to start of its current substream.
            for rng in self.problem.oracle.rng_list:
                rng.reset_substream()
        # Simulate intermediate recommended solutions.
        for mrep in range(self.n_macroreps):
            evaluated_solns = []
            for x in self.all_recommended_xs[mrep]:
                # Treat initial solution and reference solution differently.
                if x == x0:
                    evaluated_solns.append(self.initial_soln)
                elif x == xstar:
                    evaluated_solns.append(self.ref_opt_soln)
                else:
                    fresh_soln = Solution(x, self.problem)
                    self.problem.simulate(solution=fresh_soln, m=self.n_postreps)
                    evaluated_solns.append(fresh_soln)
                    if crn_across_budget is True:
                        # Reset each rng to start of its current substream.
                        for rng in self.problem.oracle.rng_list:
                            rng.reset_substream()
            # Record sequence of reevaluated solutions.
            self.all_reevaluated_solns.append(evaluated_solns)
            if crn_across_macroreps is False:
                # Advance each rng to start of
                #     substream = current substream + # of oracle RNGs.
                for rng in self.problem.oracle.rng_list:
                    for _ in range(self.problem.oracle.n_rngs):
                        rng.advance_substream()
            else:
                # Reset each rng to start of its current substream.
                for rng in self.problem.oracle.rng_list:
                    rng.reset_substream()
        # Preprocessing in anticipation of plotting.
        # Extract all unique budget points.
        repeat_budgets = [budget for budget_list in self.all_intermediate_budgets for budget in budget_list]
        self.unique_budgets = np.unique(repeat_budgets)
        self.unique_frac_budgets = self.unique_budgets / self.problem.budget
        n_inter_budgets = len(self.unique_budgets)
        # Compute signed initial optimality gap = f(x0) - f(x*);
        initial_obj_val = np.mean(self.initial_soln.objectives[:self.initial_soln.n_reps][:, 0])  # 0 <- assuming only one objective
        ref_opt_obj_val = np.mean(self.ref_opt_soln.objectives[:self.ref_opt_soln.n_reps][:, 0])  # 0 <- assuming only one objective
        initial_opt_gap = initial_obj_val - ref_opt_obj_val
        # Populate matrix containing
        #     all replicates of objective,
        #     for each macroreplication,
        #     for each budget.
        self.all_post_replicates = [[[] for _ in range(n_inter_budgets)] for _ in range(self.n_macroreps)]
        for mrep in range(self.n_macroreps):
            for budget_index in range(n_inter_budgets):
                mrep_budget_index = np.max(np.where(np.array(self.all_intermediate_budgets[mrep]) <= self.unique_budgets[budget_index]))
                lookup_solution = self.all_reevaluated_solns[mrep][mrep_budget_index]
                self.all_post_replicates[mrep][budget_index] = list(lookup_solution.objectives[:lookup_solution.n_reps][:, 0])  # 0 <- assuming only one objective
        # Store estimated objective and progress curve values
        # for each macrorep for each budget.
        self.all_est_objective = [[np.mean(self.all_post_replicates[mrep][budget_index]) for budget_index in range(n_inter_budgets)] for mrep in range(self.n_macroreps)]
        self.all_prog_curves = [[(self.all_est_objective[mrep][budget_index] - ref_opt_obj_val) / initial_opt_gap for budget_index in range(n_inter_budgets)] for mrep in range(self.n_macroreps)]
        # Save Experiment object to .pickle file.
        file_name = self.solver.name + "_on_" + self.problem.name
        record_experiment_results(experiment=self, file_name=file_name)

    def plot_progress_curves(self, plot_type, beta=0.50, normalize=True, plot_CIs=True):
        """
        Produce plots of the solver's performance on the problem.

        Arguments
        ---------
        plot_type : string
            indicates which type of plot to produce
                "all" : all estimated progress curves
                "mean" : estimated mean progress curve
                "quantile" : estimated beta quantile progress curve
        beta : float in (0,1)
            quantile to plot, e.g., beta quantile
        normalize : Boolean
            normalize progress curves w.r.t. optimality gaps?
        plot_CIs : Boolean
            plot bootstrapping confidence intervals?
        """
        # Set up plot.
        stylize_plot(plot_type=plot_type, solver_name=self.solver.name, problem_name=self.problem.name, normalize=normalize, budget=self.problem.budget, beta=beta)
        if plot_type == "all":
            # Plot all estimated progress curves.
            if normalize is True:
                for mrep in range(self.n_macroreps):
                    plt.step(self.unique_frac_budgets, self.all_prog_curves[mrep], where='post')
            else:
                for mrep in range(self.n_macroreps):
                    plt.step(self.unique_budgets, self.all_est_objective[mrep], where='post')
        elif plot_type == "mean":
            # Plot estimated mean progress curve.
            if normalize is True:
                estimator = np.mean(self.all_prog_curves, axis=0)
                plt.step(self.unique_frac_budgets, estimator, 'b-', where='post')
            else:
                estimator = np.mean(self.all_est_objective, axis=0)
                plt.step(self.unique_budgets, estimator, 'b-', where='post')
        elif plot_type == "quantile":
            # Plot estimated beta-quantile progress curve.
            if normalize is True:
                estimator = np.quantile(self.all_prog_curves, q=beta, axis=0)
                plt.step(self.unique_frac_budgets, estimator, 'b-', where='post')
            else:
                estimator = np.quantile(self.all_est_objective, q=beta, axis=0)
                plt.step(self.unique_budgets, estimator, 'b-', where='post')
        else:
            print("Not a valid plot type.")
        if plot_type == "mean" or plot_type == "quantile":
            # Report bootstrapping error estimation and optionally plot bootstrap CIs.
            self.plot_bootstrap_CIs(plot_type, normalize, estimator, plot_CIs, beta)
        save_plot(solver_name=self.solver.name, problem_name=self.problem.name, plot_type=plot_type, normalize=normalize)

    def plot_solvability_curve(self, solve_tol=0.10, plot_CIs=True):
        """
        Plot the solvability curve for a single solver-problem pair.
        Optionally plot bootstrap CIs.

        Arguments
        ---------
        solve_tol : float in (0,1]
            relative optimality gap definining when a problem is solved
        plot_CIs : Boolean
            plot bootstrapping confidence intervals?
        """
        stylize_solvability_plot(solver_name=self.solver.name, problem_name=self.problem.name, solve_tol=solve_tol)
        # Compute solve times. Ignore quantile calculations.
        self.compute_solvability_quantile(compute_CIs=False, solve_tol=solve_tol)
        # Construct matrix showing when macroreplications are solved.
        solve_matrix = np.zeros((self.n_macroreps, len(self.unique_frac_budgets)))
        # Pass over progress curves to find first solve_tol crossing time.
        for mrep in range(self.n_macroreps):
            for budget_index in range(len(self.unique_frac_budgets)):
                if self.solve_times[mrep] <= self.unique_frac_budgets[budget_index]:
                    solve_matrix[mrep][budget_index] = 1
        # Compute proportion of macroreplications "solved" by intermediate budget.
        estimator = np.mean(solve_matrix, axis=0)
        # Plot solvability curve.
        plt.step(self.unique_frac_budgets, estimator, 'b-', where='post')
        if plot_CIs is True:
            # Report bootstrapping error estimation and optionally plot bootstrap CIs.
            self.plot_bootstrap_CIs(plot_type="solvability", normalize=True, estimator=estimator, plot_CIs=plot_CIs)
        save_plot(solver_name=self.solver.name, problem_name=self.problem.name, plot_type="solvability", normalize=True)

    def compute_area_stats(self, compute_CIs=True):
        """
        Compute average and standard deviation of areas under progress curves.
        Optionally compute bootstrap confidence intervals.

        Arguments
        ---------
        compute_CIs : Boolean
            compute bootstrap confidence invervals for average and std dev?
        """
        # Compute areas under each estimated progress curve.
        self.areas = [area_under_prog_curve(prog_curve, self.unique_frac_budgets) for prog_curve in self.all_prog_curves]
        self.area_mean = np.mean(self.areas)
        self.area_std_dev = np.std(self.areas, ddof=1)
        # (Optional) Compute bootstrap CIs.
        if compute_CIs is True:
            lower_bound, upper_bound, _ = self.bootstrap_CI(plot_type="area_mean", normalize=True, estimator=[self.area_mean], n_bootstraps=100, conf_level=0.95, bias_correction=True)
            self.area_mean_CI = [lower_bound[0], upper_bound[0]]
            lower_bound, upper_bound, _ = self.bootstrap_CI(plot_type="area_std_dev", normalize=True, estimator=[self.area_std_dev], n_bootstraps=100, conf_level=0.95, bias_correction=True)
            self.area_std_dev_CI = [lower_bound[0], upper_bound[0]]

    def compute_solvability_quantile(self, compute_CIs=True, solve_tol=0.10, beta=0.50):
        """
        Compute beta quantile of alpha-solve time.
        Optionally compute bootstrap confidence intervals.

        Arguments
        ---------
        compute_CIs : Boolean
            compute bootstrap confidence invervals for quantile?
        solve_tol : float in (0,1]
            relative optimality gap definining when a problem is solved
        beta : float in (0,1)
            quantile to compute, e.g., beta quantile
        """
        self.solve_tol = solve_tol
        self.solve_times = [solve_time_of_prog_curve(prog_curve, self.unique_frac_budgets, self.solve_tol) for prog_curve in self.all_prog_curves]
        self.solve_time_quantile = np.quantile(self.solve_times, q=beta)
        # The default method for np.quantile is a *linear* interpolation.
        if compute_CIs is True:
            lower_bound, upper_bound, _ = self.bootstrap_CI(plot_type="solve_time_quantile", normalize=True, estimator=[self.solve_time_quantile], beta=beta)
            self.solve_time_quantile_CI = [lower_bound[0], upper_bound[0]]

    def bootstrap_sample(self, bootstrap_rng, crn_across_budget=True, crn_across_macroreps=False):
        """
        Generate a bootstrap sample of estimated progress curves (normalized and unnormalized).

        Arguments
        ---------
        bootstrap_rng : MRG32k3a object
            random number generator to use for bootstrapping
        crn_across_budget : bool
            use CRN for resampling postreplicates at solutions recommended at different times?
        crn_across_macroreps : bool
            use CRN for resampling postreplicates at solutions recommended on different macroreplications?

        Returns
        -------
        bootstrap_est_objective : numpy array of arrays
            bootstrapped estimated objective values of all solutions from all macroreplications
        bootstrap_prog_curves : numpy array of arrays
            bootstrapped estimated progress curves from all macroreplications
        """
        # Initialize matrices for bootstrap estimated objective and progress curves.
        bootstrap_est_objective = np.empty((self.n_macroreps, len(self.unique_budgets)))
        bootstrap_prog_curves = np.empty((self.n_macroreps, len(self.unique_budgets)))
        # Uniformly resample M macroreplications (with replacement) from 0, 1, ..., M-1.
        # Subsubstream 0: reserved for this outer-level bootstrapping.
        mreps = bootstrap_rng.choices(range(self.n_macroreps), k=self.n_macroreps)
        # Advance RNG subsubstream to prepare for inner-level bootstrapping.
        bootstrap_rng.advance_subsubstream()
        # Subsubstream 1: reserved for bootstrapping at initial solution x0 and reference optimal solution x*.
        # Bootstrap sample postreplicates at common initial solution x0.
        # Uniformly resample L postreps (with replacement) from 0, 1, ..., L.
        postreps = bootstrap_rng.choices(range(self.n_postreps_init_opt), k=self.n_postreps_init_opt)
        # Compute the mean of the resampled postreplications.
        bs_initial_obj_val = np.mean([self.initial_soln.objectives[postrep, 0] for postrep in postreps])
        # Reset subsubstream if using CRN across budgets.
        # This means the same postreplication indices will be used for resampling at x0 and x*.
        if crn_across_budget is True:
            bootstrap_rng.reset_subsubstream()
        # Bootstrap sample postreplicates at reference optimal solution x*.
        # Uniformly resample L postreps (with replacement) from 0, 1, ..., L.
        postreps = bootstrap_rng.choices(range(self.n_postreps_init_opt), k=self.n_postreps_init_opt)
        # Compute the mean of the resampled postreplications.
        bs_ref_opt_obj_val = np.mean([self.ref_opt_soln.objectives[postrep, 0] for postrep in postreps])
        # Compute initial optimality gap.
        bs_initial_opt_gap = bs_initial_obj_val - bs_ref_opt_obj_val
        # Advance RNG subsubstream to prepare for inner-level bootstrapping.
        # Will now be at start of subsubstream 2.
        bootstrap_rng.advance_subsubstream()
        # Bootstrap within each bootstrapped macroreplication.
        for bs_mrep in range(self.n_macroreps):
            mrep = mreps[bs_mrep]
            # Inner-level bootstrapping over intermediate recommended solutions.
            for budget in range(len(self.unique_budgets)):
                # If solution is x0...
                if np.array_equal(self.initial_soln.objectives[0:self.n_postreps_init_opt, 0], self.all_post_replicates[mrep][budget]):
                    # ...plug in fixed bootstrapped f(x0);
                    bootstrap_est_objective[bs_mrep][budget] = bs_initial_obj_val
                # else if solution is x*...
                elif np.array_equal(self.ref_opt_soln.objectives[0:self.n_postreps_init_opt, 0], self.all_post_replicates[mrep][budget]):
                    # ...plug in fixed bootstrapped f(x*);
                    bootstrap_est_objective[bs_mrep][budget] = bs_ref_opt_obj_val
                else:  # else solution other than x0 or x*...
                    # ...uniformly resample N postreps (with replacement) from 0, 1, ..., N-1 and ...
                    postreps = bootstrap_rng.choices(range(self.n_postreps), k=self.n_postreps)
                    # ...compute the mean of the resampled postreplications.
                    bootstrap_est_objective[bs_mrep][budget] = np.mean([self.all_post_replicates[mrep][budget][postrep] for postrep in postreps])
                # Normalize the estimated objective function value.
                bootstrap_prog_curves[bs_mrep][budget] = (bootstrap_est_objective[bs_mrep][budget] - bs_ref_opt_obj_val) / bs_initial_opt_gap
                # Reset subsubstream if using CRN across budgets.
                if crn_across_budget is True:
                    bootstrap_rng.reset_subsubstream()
            # Advance subsubstream if not using CRN across macroreps.
            if crn_across_macroreps is False:
                bootstrap_rng.advance_subsubstream()
            else:
                # Reset subsubstream if using CRN across macroreplications.
                bootstrap_rng.reset_subsubstream()
        # Advance substream of random number generator to prepare for next bootstrap sample.
        bootstrap_rng.advance_substream()
        return bootstrap_est_objective, bootstrap_prog_curves

    def bootstrap_CI(self, plot_type, normalize, estimator, n_bootstraps=100, conf_level=0.95, bias_correction=True, beta=0.50):
        """
        Construct bootstrap confidence intervals and compute max half-width.

        Arguments
        ---------
        plot_type : string
            indicates which type of plot to produce
                "mean" : estimated mean progress curve
                "quantile" : estimated beta quantile progress curve
                "area_mean" : mean of area under convergence curve
                "area_std_dev" : standard deviation of area under progress curve
                "solve_time_quantile" : beta quantile of solve time
                "solvability" : estimated solvability curve
        normalize : Boolean
            normalize progress curves w.r.t. optimality gaps?
        estimator : numpy array
            estimated mean or quantile progress curve
        n_bootstraps : int > 0
            number of times to generate a bootstrap sample of estimated progress curves
        conf_level : float in (0,1)
            confidence level for confidence intervals, i.e., 1-alpha
        bias_correction : bool
            use bias-corrected bootstrap CIs (via percentile method)?
        beta : float in (0,1)
            quantile for quantile aggregate progress curve, e.g., beta quantile

        Returns
        -------
        bs_CI_lower_bounds : numpy array
            lower bounds of bootstrap CIs at all budgets
        bs_CI_upper_bounds : numpy array
            upper bounds of bootstrap CIs at all budgets
        max_halfwidth : float
            maximum halfwidth of all bootstrap confidence intervals constructed
        """
        # Create random number generator for bootstrap sampling.
        # Stream 1 dedicated for bootstrapping.
        bootstrap_rng = MRG32k3a(s_ss_sss_index=[1, 0, 0])
        if plot_type == "mean" or plot_type == "quantile" or plot_type == "solvability":
            n_intervals = len(self.unique_budgets)
        elif plot_type == "area_mean" or plot_type == "area_std_dev" or plot_type == "solve_time_quantile":
            n_intervals = 1
        bs_aggregate_objects = np.zeros((n_bootstraps, n_intervals))
        for bs_index in range(n_bootstraps):
            # Generate bootstrap sample of estimated progress curves.
            bootstrap_est_objective, bootstrap_prog_curves = self.bootstrap_sample(bootstrap_rng=bootstrap_rng, crn_across_budget=True, crn_across_macroreps=False)
            # Apply the functional of the bootstrap sample,
            # e.g., mean/quantile (aggregate) progress curve.
            if plot_type == "mean":
                if normalize is True:
                    bs_aggregate_objects[bs_index] = np.mean(bootstrap_prog_curves, axis=0)
                else:
                    bs_aggregate_objects[bs_index] = np.mean(bootstrap_est_objective, axis=0)
            elif plot_type == "quantile":
                if normalize is True:
                    bs_aggregate_objects[bs_index] = np.quantile(bootstrap_prog_curves, q=beta, axis=0)
                else:
                    bs_aggregate_objects[bs_index] = np.quantile(bootstrap_est_objective, q=beta, axis=0)
            elif plot_type == "area_mean":
                areas = [area_under_prog_curve(prog_curve, self.unique_frac_budgets) for prog_curve in bootstrap_prog_curves]
                bs_aggregate_objects[bs_index] = np.mean(areas)
            elif plot_type == "area_std_dev":
                areas = [area_under_prog_curve(prog_curve, self.unique_frac_budgets) for prog_curve in bootstrap_prog_curves]
                bs_aggregate_objects[bs_index] = np.std(areas, ddof=1)
            elif plot_type == "solve_time_quantile":
                solve_times = [solve_time_of_prog_curve(prog_curve, self.unique_frac_budgets, self.solve_tol) for prog_curve in bootstrap_prog_curves]
                bs_aggregate_objects[bs_index] = np.quantile(solve_times, q=beta)
            elif plot_type == "solvability":
                solve_times = [solve_time_of_prog_curve(prog_curve, self.unique_frac_budgets, self.solve_tol) for prog_curve in bootstrap_prog_curves]
                # Construct full matrix showing when macroreplications are solved.
                solve_matrix = np.zeros((self.n_macroreps, len(self.unique_frac_budgets)))
                # Pass over progress curve to find first solve_tol crossing time.
                for mrep in range(self.n_macroreps):
                    for budget_index in range(len(self.unique_frac_budgets)):
                        if solve_times[mrep] <= self.unique_frac_budgets[budget_index]:
                            solve_matrix[mrep][budget_index] = 1
                bs_aggregate_objects[bs_index] = np.mean(solve_matrix, axis=0)

        # Compute bootstrapping confidence intervals via percentile method.
        # See Efron and Gong (1983) "A leisurely look at the bootstrap,
        #     the jackknife, and cross-validation."
        if bias_correction is True:
            # For biased-corrected CIs, see equation (17) on page 41.
            z0s = [norm.ppf(np.mean(bs_aggregate_objects[:, interval_id] < estimator[interval_id])) for interval_id in range(n_intervals)]
            zconflvl = norm.ppf(conf_level)
            q_lowers = [norm.cdf(2 * z0 - zconflvl) for z0 in z0s]
            q_uppers = [norm.cdf(2 * z0 + zconflvl) for z0 in z0s]
            bs_CI_lower_bounds = np.array([np.quantile(bs_aggregate_objects[:, interval_id], q=q_lowers[interval_id]) for interval_id in range(n_intervals)])
            bs_CI_upper_bounds = np.array([np.quantile(bs_aggregate_objects[:, interval_id], q=q_uppers[interval_id]) for interval_id in range(n_intervals)])
        else:
            # For uncorrected CIs, see equation (16) on page 41.
            q_lower = (1 - conf_level) / 2
            q_upper = 1 - (1 - conf_level) / 2
            bs_CI_lower_bounds = np.quantile(bs_aggregate_objects, q=q_lower, axis=0)
            bs_CI_upper_bounds = np.quantile(bs_aggregate_objects, q=q_upper, axis=0)
        max_halfwidth = np.max((bs_CI_upper_bounds - bs_CI_lower_bounds) / 2)
        return bs_CI_lower_bounds, bs_CI_upper_bounds, max_halfwidth

    def plot_bootstrap_CIs(self, plot_type, normalize, estimator, plot_CIs,
                           beta=None):
        """
        Optionally plot bootstrap confidence intervals and report max
        half-width.

        Arguments
        ---------
        plot_type : string
            indicates which type of plot to produce
                "all" : all estimated progress curves
                "mean" : estimated mean progress curve
                "quantile" : estimated beta quantile progress curve
                "solvability" : estimated solvability curve
        normalize : Boolean
            normalize progress curves w.r.t. optimality gaps?
        estimator : numpy array
            estimated mean or quantile progress curve
        plot_CIs : Boolean
            plot bootstrapping confidence intervals?
        beta : float in (0,1) (optional)
            quantile for quantile aggregate progress curve, e.g., beta quantile
        """
        # Construct bootstrap confidence intervals.
        bs_CI_lower_bounds, bs_CI_upper_bounds, max_halfwidth = self.bootstrap_CI(plot_type=plot_type, normalize=normalize, estimator=estimator, beta=beta)
        if normalize is True:
            budgets = self.unique_frac_budgets
            xloc = 0.05
            yloc = -0.35
        else:
            budgets = self.unique_budgets
            xloc = 0.05 * self.problem.budget
            yloc = (min(bs_CI_lower_bounds)
                    - 0.25 * (max(bs_CI_upper_bounds) - min(bs_CI_lower_bounds)))
        if plot_CIs is True:
            # Optionally plot bootstrap confidence intervals.
            plt.step(budgets, bs_CI_lower_bounds, 'b--', where='post')
            plt.step(budgets, bs_CI_upper_bounds, 'b--', where='post')
        # Print caption about max halfwidth of bootstrap confidence intervals.
        txt = ("The max halfwidth of the bootstrap CIs is "
               + str(round(max_halfwidth, 2)) + ".")
        plt.text(x=xloc, y=yloc, s=txt)


def record_experiment_results(experiment, file_name):
    """
    Save wrapper_base.Experiment object to .pickle file.

    Arguments
    ---------
    experiment : wrapper_base.Experiment object
        Experiment object to pickle
    file_name : string
        base name of pickle file to write outputs to
    """
    with open("experiments/outputs/" + file_name + ".pickle", "wb") as file:
        pickle.dump(experiment, file, pickle.HIGHEST_PROTOCOL)


def read_experiment_results(file_name):
    """
    Read in wrapper_base.Experiment object from .pickle file.

    Arguments
    ---------
    file_name : string
        base name of pickle file from which to read in outputs

    Returns
    -------
    experiment : wrapper_base.Experiment object
        experiment that has been run or has been post-processed
    """
    with open("experiments/outputs/" + file_name + ".pickle", "rb") as file:
        experiment = pickle.load(file)
    return experiment


def stylize_plot(plot_type, solver_name, problem_name, normalize, budget=None,
                 beta=None):
    """
    Create new figure. Add labels to plot and reformat axes.

    Arguments
    ---------
    plot_type : string
        indicates which type of plot to produce
            "all" : all estimated progress curves
            "mean" : estimated mean progress curve
            "quantile" : estimated beta quantile progress curve
    solver_name : string
        name of solver
    problem_name : string
        name of problem
    normalize : Boolean
        normalize progress curves w.r.t. optimality gaps?
    budget : int
        budget of problem, measured in function evaluations
    beta : float in (0,1) (optional)
        quantile for quantile aggregate progress curve, e.g., beta quantile
    """
    plt.figure()
    # Format axes, axis labels, title, and tick marks.
    if normalize is True:
        xlabel = "Fraction of Budget"
        ylabel = "Fraction of Initial Optimality Gap"
        xlim = (0, 1)
        ylim = (-0.1, 1.1)
        title = solver_name + " on " + problem_name + "\n"
    elif normalize is False:
        xlabel = "Budget"
        ylabel = "Objective Function Value"
        xlim = (0, budget)
        ylim = None
        title = solver_name + " on " + problem_name + "\n" + "Unnormalized "
    if plot_type == "all":
        title = title + "Estimated Progress curves"
    elif plot_type == "mean":
        title = title + "Mean Progress curve"
    elif plot_type == "quantile":
        title = title + str(round(beta, 2)) + "-Quantile Progress Curve"
    plt.xlabel(xlabel, size=14)
    plt.ylabel(ylabel, size=14)
    plt.title(title, size=14)
    plt.xlim(xlim)
    if ylim is not None:
        plt.ylim(ylim)
    plt.tick_params(axis='both', which='major', labelsize=12)


def stylize_solvability_plot(solver_name, problem_name, solve_tol=0.50):
    """
    Create new figure. Add labels to plot and reformat axes.

    Arguments
    ---------
    solver_name : string
        name of solver
    problem_name : string
        name of problem
    normalize : Boolean
        normalize progress curves w.r.t. optimality gaps?
    budget : int
        budget of problem, measured in function evaluations
    """
    plt.figure()
    # Format axes, axis labels, title, and tick marks.
    xlabel = "Fraction of Budget"
    ylabel = "Fraction of Macroreplications Solved"
    xlim = (0, 1)
    ylim = (0, 1)
    title = solver_name + " on " + problem_name + "\n"
    title = title + str(round(solve_tol, 2)) + "-Solvability Curve"
    plt.xlabel(xlabel, size=14)
    plt.ylabel(ylabel, size=14)
    plt.title(title, size=14)
    plt.xlim(xlim)
    if ylim is not None:
        plt.ylim(ylim)
    plt.tick_params(axis='both', which='major', labelsize=12)


def save_plot(solver_name, problem_name, plot_type, normalize):
    """
    Create new figure. Add labels to plot and reformat axes.

    Arguments
    ---------
    solver_name : string
        name of solver
    problem_name : string
        name of problem
    plot_type : string
        indicates which type of plot to produce
            "all" : all estimated progress curves
            "mean" : estimated mean progress curve
            "quantile" : estimated beta quantile progress curve
            "solvability" : estimated solvability curve
    normalize : Boolean
        normalize progress curves w.r.t. optimality gaps?
    """
    # Form string name for plot filename.
    if plot_type == "all":
        plot_name = "all_prog_curves"
    elif plot_type == "mean":
        plot_name = "mean_prog_curve"
    elif plot_type == "quantile":
        plot_name = "quantile_prog_curve"
    elif plot_type == "solvability":
        plot_name = "solvability_curve"
    if normalize is False:
        plot_name = plot_name + "_unnorm"
    path_name = "experiments/plots/" + str(solver_name) + "_on_" + str(problem_name) + "_" + plot_name + ".png"
    plt.savefig(path_name, bbox_inches="tight")


def area_under_prog_curve(prog_curve, frac_inter_budgets):
    """
    Compute the area under a normalized estimated progress curve.

    Arguments
    ---------
    prog_curve : numpy array
        normalized estimated progress curve for a macroreplication
    frac_inter_budgets : numpy array
        fractions of budget at which the progress curve is defined

    Returns
    -------
    area : float
        area under the estimated progress curve
    """
    area = np.dot(prog_curve[:-1], np.diff(frac_inter_budgets))
    return area


def solve_time_of_prog_curve(prog_curve, frac_inter_budgets, solve_tol):
    """
    Compute the solve time of a normalized estimated progress curve.

    Arguments
    ---------
    prog_curve : numpy array
        normalized estimated progress curves for a macroreplication
    frac_inter_budgets : numpy array
        fractions of budget at which the progress curve is defined
    solve_tol : float in (0,1]
        relative optimality gap definining when a problem is solved

    Returns
    -------
    solve_time : float
        time at which the normalized progress curve first drops below
        solve_tol, i.e., the "alpha" solve time
    """
    # Alpha solve time defined as infinity if the problem is not solved
    # to within solve_tol.
    solve_time = np.inf
    # Pass over progress curve to find first solve_tol crossing time.
    for i in range(len(prog_curve)):
        if prog_curve[i] < solve_tol:
            solve_time = frac_inter_budgets[i]
            break
    return solve_time


class MetaExperiment(object):
    """
    Base class for running one or more solver on one or more problem.

    Attributes
    ----------
    solver_names : list of strings
        list of solver names
    problem_names : list of strings
        list of problem names
    all_solver_fixed_factors : dict of dict
        fixed solver factors for each solver
            outer key is solver name
            inner key is factor name
    all_problem_fixed_factors : dict of dict
        fixed problem factors for each problem
            outer key is problem name
            inner key is factor name
    all_oracle_fixed_factors : dict of dict
        fixed oracle factors for each problem
            outer key is problem name
            inner key is factor name
    experiments : list of list of Experiment objects
        all problem-solver pairs

    Arguments
    ---------
    solver_names : list of strings
        list of solver names
    problem_names : list of strings
        list of problem names
    fixed_factors_filename : string
        name of .py file containing dictionaries of fixed factors
        for solvers/problems/oracles.
    """
    def __init__(self, solver_names, problem_names, fixed_factors_filename=None):
        self.solver_names = solver_names
        self.problem_names = problem_names
        # Read in fixed solver/problem/oracle factors from .py file in the Experiments folder.
        # File should contain three dictionaries of dictionaries called
        #   - all_solver_fixed_factors
        #   - all_problem_fixed_factors
        #   - all_oracle_fixed_factors
        fixed_factors_filename = "experiments.inputs." + fixed_factors_filename
        all_factors = importlib.import_module(fixed_factors_filename)
        self.all_solver_fixed_factors = getattr(all_factors, "all_solver_fixed_factors")
        self.all_problem_fixed_factors = getattr(all_factors, "all_problem_fixed_factors")
        self.all_oracle_fixed_factors = getattr(all_factors, "all_oracle_fixed_factors")
        # Create all problem-solver pairs (i.e., instances of Experiment class)
        self.experiments = []
        for solver_name in solver_names:
            solver_experiments = []
            for problem_name in problem_names:
                try:
                    # If a file exists, read in Experiment object.
                    with open("experiments/outputs/" + solver_name + "_on_" + problem_name + ".pickle", "rb") as file:
                        next_experiment = pickle.load(file)
                    # TO DO: Check if the solver/problem/oracle factors in the file match
                    # those for the MetaExperiment.
                except:
                    # If no file exists, create new Experiment object.
                    print("No experiment file exists for " + solver_name + " on " + problem_name + ". Creating new experiment.")
                    next_experiment = Experiment(solver_name=solver_name,
                                                problem_name=problem_name,
                                                solver_fixed_factors=self.all_solver_fixed_factors[solver_name],
                                                problem_fixed_factors=self.all_problem_fixed_factors[problem_name],
                                                oracle_fixed_factors=self.all_oracle_fixed_factors[problem_name])
                    # Save Experiment object to .pickle file.
                    file_name = solver_name + "_on_" + problem_name
                    record_experiment_results(experiment=next_experiment, file_name=file_name)
                solver_experiments.append(next_experiment)
            self.experiments.append(solver_experiments)
