"""
This module implements the class BBOptimizer, which is the interface that allows to optimize a
black-box with a given heuristic, which is passed as a string. Given a "black-box" instance,
which is simply defined as a Python object with a compute method, the optimize method of the
BBOptimizer runs the heuristic and looks for the optimum of the function. The starting data
points of the optimizer are selected using initial parametrisation methods taken from the
literature.

This class also offers some summary measures to inform the user about the process:
- Interactive virtual representations of the optimization process
- Various metrics that describe the optimization process

All of the potentially available heuristics are described in the __heuristics__ dictionary and
the available initialization in __initial_parametrization__.
"""

import time
import contextlib
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from devtools import debug

from bbo.heuristics.surrogate_models.surrogate_models import SurrogateModel
from bbo.heuristics.simulated_annealing.simulated_annealing import SimulatedAnnealing
from bbo.heuristics.genetic_algorithm.genetic_algorithm import GeneticAlgorithm
from bbo.heuristics.exhaustive_search.exhaustive_search import ExhaustiveSearch
from bbo.initial_parametrizations import (
    uniform_random_draw,
    latin_hypercube_sampling,
    hybrid_lhs_uniform_sampling,
)
from bbo.noise_reduction.resampling_policies import (
    SimpleResampling,
    DynamicResamplingParametric,
    DynamicResamplingParametric2,
    DynamicResamplingNonParametric,
    DynamicResamplingNonParametric2,
)
from bbo.noise_reduction.fitness_transformation import (
    FitnessTransformation,
    SimpleFitnessTransformation,
)


class BBOptimizer:
    """
    Interface that allows to optimize a black-box with a given heuristic.
    """

    # Dictionary of the heuristics that can be used with the optimizer
    __heuristics__ = {
        "surrogate_model": SurrogateModel,
        "simulated_annealing": SimulatedAnnealing,
        "genetic_algorithm": GeneticAlgorithm,
        "exhaustive_search": ExhaustiveSearch,
    }

    # Dictionary of the different methods that can be used to sample the initial parameters
    __initial__parametrization__ = {
        "uniform_random": uniform_random_draw,
        "latin_hypercube_sampling": latin_hypercube_sampling,
        "hybrid_lhs_uniform_sampling": hybrid_lhs_uniform_sampling,
    }

    # Dictionary of the different resampling policies
    __resampling_policies__ = {
        "simple_resampling": SimpleResampling,
        "dynamic_resampling": DynamicResamplingParametric,
        "dynamic_resampling_2": DynamicResamplingParametric2,
        "dynamic_resampling_non_parametric": DynamicResamplingNonParametric,
        "dynamic_resampling_non_parametric_2": DynamicResamplingNonParametric2,
    }

    # Dictionnary of the different fitness aggregation strategies
    __fitness_aggregation__ = {
        "simple_fitness_aggregation": SimpleFitnessTransformation
    }

    def __init__(
        self,
        black_box,
        parameter_space,
        heuristic,
        time_out=None,
        max_iteration=100,
        perf_function=None,
        initial_sample_size=10,
        initial_draw_method="hybrid_lhs_uniform_sampling",
        reevaluate=True,
        max_retry=5,
        async_optim=False,
        max_step_cost=None,
        resampling_policy=None,
        fitness_aggregation=None,
        **kwargs,
    ):
        """
        Initialization of the BBOptimizer class which performs black-box optimization of a
        black-box function, represented by a Python object which possess a 'compute()' method.
        Args:
          black_box (python object): This is a python object that must have a `.compute()` method
            defined, else an error is raised.

          parameter_space (numpy array of numpy arrays): A numpy array of numpy arrays,
            each representing the grid of possible parameters in each dimension.

          perf_function: Optionally transform the output of black_box.compute() into a numeric cost
            value that can be used instead of the original output when performing optimization.

          heuristic (str): The heuristic method to use when searching for parameters. They are
            listed in the __heuristics__ dictionary.

          time_out (float): Maximum elapsed time (in seconds) for optimization.

          max_iteration (int): Maximum number of iterations in self-optimization loop.
            Defaults to 100.

          reevaluate (bool): Whether or not a value can be re-evaluted if it has already
            been evaluated by the algorithm. Closely depends on max_retry which indicates how many
            times the algorithm which performs the next parameter selection has to be launched
            again.

          max_retry (int): Maximum number of retries of the next parameter selection algorithm when
            reevaluation is set to false.

          async_optim (bool): Whether or not the optimization should be done asynchronously, by
            sending the computation in another process. This allows to prune parametrization that
            take longer to compute than others. By default, the monitoring function is simply the
            time spent by the process for computing. More complex functions can be passed as an option
            in step_cost_function method of the black-box. By default, the computation is stopped simply by killing the
            multiprocess, but more complex options can be passed as the method .on_interrupt() of the
            black-box.

          max_step_cost (float): Maximum value the cost function can take before calling the .kill
            method of the black-box. It can be set to a function, which dynamically computes the
            max step cost at each iteration.
          resampling_strategy (str, optional): The optional resampling strategy to use. A resampling
            strategy consists in evaluating several times the parametrizations in order to get a
            better estimate of the fitness function for this parametrization. The possible
            resampling strategies are located in the dictionary __resampling_policies__.
            Defaults to no resampling.

          fitness_aggregation (str, optional): The transformation to apply to the fitness function
            when some parametrization have been evaluated more than once. The possible fitness
            aggregation strategies are located in the dictionary __fitness_aggregation__?
            Defaults to performing a simple aggregation using the mean as the estimator.

        Other arguments which are specific to the selected heuristics can be passed upon
        initialization of the object.
        """
        # Store black_box application
        self.black_box = black_box

        # Check for the compute method
        if not hasattr(self.black_box, "compute"):
            raise AttributeError(
                f"Object {black_box} does not have a method named `compute` "
                f"defined."
            )

        # Handle output transformation function
        if perf_function is None:
            self.compute_result = self.black_box.compute
        else:
            self.compute_result = lambda x: perf_function(self.black_box.compute(x))
        # Instantiate empty history
        self.history = {
            "fitness": None,
            "parameters": None,
            "truncated": None,
            "resampled": None,
            "initialization": None,
        }

        # Store stop criteria (if specified)
        self.time_out = time_out
        self.max_iteration = max_iteration

        # Store reevaluation criteria
        # If the reevaluation option is set to true, set the max_retry to 1 in order to launch
        # the optimization algorithm once per iteration
        if reevaluate:
            self.max_retry = 1
        else:
            self.max_retry = max_retry

        # Store options for the heuristic and the noise reduction policies
        self.options = kwargs

        # Ensure heuristic is valid and create corresponding object
        try:
            self.heuristic = self.__heuristics__[heuristic](**self.options)
        except KeyError:
            raise ValueError(
                "You must provide a valid value for heuristic argument."
                f"You can choose among {self.__heuristics__.keys()}"
            )
        except Exception as exception:
            raise Exception(
                f"Missing argument upon heuristic initialization: {str(exception)}"
            )

        # Ensure initial selections are valid and store the method into an attribute
        try:
            self.initial_selection = self.__initial__parametrization__[
                initial_draw_method
            ]
        except KeyError:
            raise ValueError(
                f"{initial_draw_method} is not among possible choices.\
                fYou can choose among {self.__initial__parametrization__.keys()}"
            )
        # Store initial sample size
        self.initial_sample_size = initial_sample_size

        # Store initial parameter space
        self.parameter_space = parameter_space

        # Store whether or not the computations happens asynchronously
        self.async_optimization = async_optim
        # Store the max step, if not specified, set it to inf
        self.max_step_cost = max_step_cost
        if not self.max_step_cost:
            self.max_step_cost = np.inf
        # Check if the black-box comes with a custom on_interrupt method,
        # else, put None in the field
        if hasattr(self.black_box, "on_interrupt"):
            self.on_interrupt = self.black_box.on_interrupt
        else:
            self.on_interrupt = None
        # Store the cost function if there is any
        if hasattr(self.black_box, "cost_function"):
            self.step_cost_function = self.black_box.cost_function
        else:
            self.step_cost_function = None
        # If there is a resampling strategy, ensure that it is valid
        # If there is no resampling strategy, set it to simple with
        # a resampling number of 1
        if resampling_policy:
            try:
                self.resampling_policy = self.__resampling_policies__[
                    resampling_policy
                ](**self.options)
            except KeyError:
                raise ValueError(
                    f"{resampling_policy} is not among possible choices."
                    f"Possible choices are {self.__resampling_policies__.keys()}"
                )
        else:
            self.resampling_policy = SimpleResampling(nbr_resamples=1)

        # If there is a fitness aggregation strategy, ensure that it is valid
        # If there is none, defaults to simple with the mean estimator
        if fitness_aggregation:
            try:
                self.fitness_aggregation = self.__fitness_aggregation__[
                    fitness_aggregation
                ](**self.options)
            except KeyError:
                raise ValueError(
                    f"{resampling_policy} is not among possible choices."
                    f"Possible choices are {self.__fitness_aggregation__.keys()}"
                )
        else:
            self.fitness_aggregation = FitnessTransformation()
        # Set two values: the number of iterations and the elapsed time for the computation
        self.nbr_iteration = 0
        self.elapsed_time = 0

        # Boolean that will inform if the black box has been optimized.
        self.launched = False

        # Optimum parameters found during optimization process
        self.best_parameters_in_grid = None
        # Optimum fitness found
        self.best_fitness = None

    def _append_parameters(self, new_parameters):
        """
        Appends new parameters to the history of previously selected parameters, by stacking the
        new on the old parameters.

        Args:
            new_parameters (numpy array): The parameters to append to the history.

        Returns:
            None, modifies the field "parameters" of the history attribute
        """
        # If there are some values already in the history
        if self.history["parameters"] is not None:
            self.history["parameters"] = np.vstack(
                [self.history["parameters"], new_parameters]
            )
        # Else
        else:
            self.history["parameters"] = new_parameters

    def _append_fitness(self, new_fitness):
        """
        Appends new parameters to the history of previously evaluated performance, by stacking the
        new on the old performance.

        Args:
            new_fitness (float): The performance to append to the history.

        Returns:
            None, modifies the field "fitness" of the history attribute
        """
        if self.history["fitness"] is not None:
            self.history["fitness"] = np.append(self.history["fitness"], new_fitness)
        else:
            self.history["fitness"] = [new_fitness]

    def _append_truncated(self, new_truncated):
        """
        Appends new parameters to the history of previously evaluated performance, by stacking the
        new on the old performance.

        Args:
            new_fitness (float): The performance to append to the history.

        Returns:
            None, modifies the field "fitness" of the history attribute
        """
        if self.history["truncated"] is not None:
            self.history["truncated"] = np.append(
                self.history["truncated"], new_truncated
            )
        else:
            self.history["truncated"] = [new_truncated]

    def _append_resampled(self, new_resampled):
        """
        Appends new parameters to the history of previously evaluated performance, by stacking the
        new on the old performance.

        Args:
            new_resampled (float): The performance to append to the history.

        Returns:
            None, modifies the field "fitness" of the history attribute
        """
        if self.history["resampled"] is not None:
            self.history["resampled"] = np.append(
                self.history["resampled"], new_resampled
            )
        else:
            self.history["resampled"] = [new_resampled]

    def _append_init(self, new_initialization):
        """
        Appends new parameters to the history of whether or not the optimization step was an
        initialization one.

        Args:
            new_initialization (bool): The performance to append to the history.

        Returns:
            None, modifies the field "init" of the history attribute
        """
        if self.history["initialization"] is not None:
            self.history["initialization"] = np.append(
                self.history["initialization"], new_initialization
            )
        else:
            self.history["initialization"] = [new_initialization]

    @property
    def stop_rule(self):
        """
        Creates the rule to stop the while loop. It takes into account the number of iterations
        and the elapsed time for the heuristic, as well as the internal heuristic stop criterion. If
        any of these conditions are met, the loop stops.

        Returns:
            bool: A boolean which represents whether or not to stop the black box optimizing loop.
        """
        conditions = list()
        if self.max_iteration:
            conditions.append(self.nbr_iteration < self.max_iteration)
        if self.time_out:
            conditions.append(self.elapsed_time < self.time_out)
        if self.heuristic.stop:
            conditions.append(not self.heuristic.stop)
        return all(conditions)

    def _async_optimization_step(self, parameter):
        """
        Performs the optimization step asynchrously, in order to timeit
        and interrupt it if it spends too much time computing.

        Args:
            parameter (numpy array): the parameter to evaluate.
        """
        # Set the truncated value as False
        truncated = False
        # If the max step cost is dynamic, set it to the median value
        if callable(self.max_step_cost):
            max_step_cost = self.max_step_cost(self.history["fitness"])
        else:
            max_step_cost = self.max_step_cost
        # Open a separate thread
        pool = ThreadPoolExecutor()
        computing_thread = pool.submit(self.compute_result, (parameter))
        start_time = time.time()
        while not computing_thread.done():
            # If there is no cost function, use the time as default
            # Else, use the function passed by the user
            if self.step_cost_function:
                cost = self.step_cost_function()
            else:
                cost = time.time() - start_time
            if cost < max_step_cost:
                time.sleep(0.1)
            else:
                # End the process
                computing_thread.cancel()
                # If there is a on_interrupt method of the black-box,
                # call it
                if self.on_interrupt:
                    self.on_interrupt()
                # Store the value as truncated
                truncated = True
                break
        if truncated:
            perf = max_step_cost
        else:
            perf = computing_thread.result()

        # Store the parameters
        self._append_parameters(parameter)
        # Store the fitness
        self._append_fitness(perf)
        # Store the value as not truncated
        self._append_truncated(truncated)

    def _optimization_step(self, parameter):
        """
        Performs a single optimization step, which consists in:
            - Evaluating the fitness for parameter 'parameter'
            - Appending the new value to history of optimization (fitness and tested parameters)
            - Calling optional callbacks on the history attribute of the class
        Args:
            parameter: The parameter to evaluate at this step.
            callback: A list of functions to call on the history attribute of
                the optimization at each iteration.

        Returns:
            None, but applies the callback on the history attribute of the class
        """
        debug(f"Evaluating performance of parametrization {parameter}")
        # evaluate the value of the newly selected parameters
        perf = self.compute_result(parameter)
        debug(f"Corresponding performance: {perf}")
        # store the new parameters
        self._append_parameters(parameter)
        # store the new performance
        self._append_fitness(perf)
        # store the value as non truncated
        self._append_truncated(False)

    def _initialize(self, callbacks=[lambda x: x]):
        """
        Initalizes the black-box algorithm using the selected strategy and the
        number of initial data points.
        """
        debug("Initializing parameter space")
        debug(f"Parameter space: {self.parameter_space}")
        # Draw parameters according to the initialization method and compute fitness value
        initial_parameters = self.initial_selection(
            self.initial_sample_size, self.parameter_space
        )
        debug("Selected parameter space: {initial_parameters}")
        step = 0
        while step < self.initial_sample_size:
            # Perform optimization step using the initial parametrization
            self._optimization_step(parameter=initial_parameters[step])
            # store as non resampled
            self._append_resampled(False)
            # store as init
            self._append_init(True)
            # call callbacks
            for callback in callbacks:
                callback(self.history)
            # update number of iterations and elapsed time
            step += 1

    def _get_best_performance(self):
        """
        Get the best performance of a given history.

        Returns:
            tuple: the best parameter and the corresponding best performance
        """
        # Transform history
        transformed_history = self.fitness_aggregation.transform(self.history)
        # Sort according to best performance (eg: minimal fitness), if at least two elements
        if len(transformed_history["fitness"]) > 1:
            sorted_perf_idx = transformed_history["fitness"].argsort()
            sorted_perf = transformed_history["fitness"][sorted_perf_idx[::-1]]
            sorted_parameters = transformed_history["parameters"][sorted_perf_idx[::-1]]
            # Return the last parameters which corresponds to the best performance
            return sorted_parameters[-1], sorted_perf[-1]
        # Else, return the unsorted parameter and history
        else:
            return transformed_history["parameters"], transformed_history["fitness"][0]

    @staticmethod
    def closest_parameters(parameters, parametric_space):
        """
        Compute the parameters that are the closest (in the L1 sense) on the parametric_space to
        the parameter given in argument.

        Args:
            parameter (numpy array): The parameter for which to find the closest neighbor.
            parametric_space (numpy array of arrays): The possible value for the parameters in
                each dimension.

        Returns:
            numpy array: The closest parameter in the grid.
        """
        best_parameters_in_grid = list()
        for axis in range(parametric_space.shape[0]):
            arg_min = np.argmin(np.abs(parameters[axis] - parametric_space[axis]))
            best_parameters_in_grid.append(parametric_space[axis][arg_min])
        return np.array(best_parameters_in_grid)

    def _choose_next_parameters(self, current_parameters=None):
        """
        Wrapper around the .choose_next_parameter method of the heuristic
        attribute. This ensures that the result is constrained to the
        optimization grid. This method gets the parametrization suggested
        by the attribute and then returns the closest parametrization on the grid.

        Args:
            current_parameters (np.array): The parametrization to start the optimization process on.
                Defaults to None, which corresponds to the last evaluated parametrization.

        Returns:
            np.array: The parameters constrained to the grid.
        """
        aggregated_history = self.fitness_aggregation.transform(self.history)
        parameter_returned_by_heuristic = self.heuristic.choose_next_parameter(
            aggregated_history,
            self.parameter_space,
            current_parameters=current_parameters,
        )
        return self.closest_parameters(
            parameter_returned_by_heuristic, self.parameter_space
        )

    def _select_next_parameters(self, current_parameters=None):
        """
        Select the next parameters to be evaluated by the algorithm,
        by using the following workflow:
            - Get the parameter using the wrapper around
                the heuristic selecion process _choose_next_parameters method
            - If the reevaluate function is set to false (offline optimization setting),
                make sure that the selected parameter is different from already tested
                parameterizations.
                If it is not different, run the algorithm again, with a maximum
                of allowed retries set to self.max_retry
            - If there is a resampling policy, check if the last parameter should be
                re-evaluated or not

        Args:
            current_parameters (np.array): The parametrization to start the optimization process on.
                Defaults to None, which corresponds to the last evaluated parametrization.

        Return:
            parameters (np.array): The newly selected parameters.
        """
        # If resampling is enabled, check that there have been enough repetitions
        if self.resampling_policy.resample(self.history):
            # Set resampled to True
            self._append_resampled(True)
            return self.history["parameters"][-1]
        # Set resampled to false
        self._append_resampled(False)
        # apply optimizer on history and constrain it to the parameter grid
        parameters = self._choose_next_parameters(current_parameters)
        # if retry is enabled, call several times the choose_next_parameter function
        # if reevaluate is set to false, the cntr is set to 1 and the loop is repeated
        # only once
        if self.max_retry > 1:
            cntr = 0
            while (
                np.equal(self.history["parameters"], parameters).all(axis=1).any()
                and cntr < self.max_retry
            ):
                parameters = self._choose_next_parameters()
                cntr += 1
        return parameters

    def optimize(self, callbacks=[lambda x: x]):
        """
        Performs the optimization process and saves the optimization results as attributes of the
        class.

        The workflow is the following:
            - Choose the initial parameters using the initialization strategy

            - While the stop criterion has not been met:
                - Apply black box function on current parameter
                - Save the parameters and the corresponding fitness in the heuristic history
                - launch heuristic with the enhanced history
        """
        # start chronometer at beginning of experiment
        chronometer_start = time.time()
        # Perform initialization
        self._initialize(callbacks)
        # Store last parameter in current_parameters variable
        current_parameters, _ = self._get_best_performance()
        # Initialize the loop with one data point
        current_parameters = self._select_next_parameters(current_parameters)
        # while the stop criterion has not yet been met
        while self.stop_rule:
            # Perform optimization step, either synchronously or asynchronously
            if self.async_optimization:
                self._async_optimization_step(current_parameters)
            else:
                self._optimization_step(current_parameters)
            # Add the optimization step as non-init
            self._append_init(False)
            # Select the next parameter to evaluate
            current_parameters = self._select_next_parameters()
            # call callback on the history
            for callback in callbacks:
                callback(self.history)
            # update number of iterations
            self.nbr_iteration += 1
        self.elapsed_time = time.time() - chronometer_start
        # Store the best parameters and the best fitness
        self.best_parameters_in_grid, self.best_fitness = self._get_best_performance()
        # set launched variable to true value
        self.launched = True
        return self.best_parameters_in_grid

    def summarize(self):
        """
        Prints the summary of the optimization loop.
        """
        if not self.launched:
            raise Exception(
                "Black box has not been optimized yet. Please run the .optimize "
                "method before requesting a summary."
            )
        print("------ Optimization loop summary ------")
        print(f"Number of iterations: {self.total_iteration}")
        print(f"Elapsed time: {self.elapsed_time}")
        print(f"Best parameters: {self.best_parameters_in_grid}")
        print(f"Best fitness value: {self.best_fitness}")
        print(f"Percentage of explored space: {self.size_explored_space[0]}")
        print(f"Percentage of static moves: {self.size_explored_space[1]}")
        print(f"Cost of global exploration: {self.global_exploration_cost[1]}")
        print(
            f"Mean fitness gain per iteration: {np.mean(self.fitness_gain_per_iteration)}"
        )
        print(
            f"Number of iterations until best fitness: {self.nbr_iteration_best_fitness}"
        )
        print(f"Average variation within each parametrization: {self.measured_noise}")
        print(f"--- Heuristic specific summary ---")
        print(f"{self.heuristic.summary(self.history)}")

    def _compute_consecutive_aggregation(self, estimator):
        """Given an estimator, computes the aggregated values per consecutive parametrization.

        Args:
            estimator (function): A function to compute the aggregation, that can be vectorized

        """
        # = list()
        fitness_array = np.array(self.history["fitness"])
        parameters_array = np.array(self.history["parameters"])
        # Get the index of the unique parametrization
        # You have to use the index else the array gets sorted and this is problematic
        # for space location dependent heuristics
        ix = 1
        consecutives = list()
        consecutive_per_parametrization = [fitness_array[ix - 1]]
        while ix < (parameters_array.shape[0]):
            if np.all(parameters_array[ix - 1] == parameters_array[ix]):
                consecutive_per_parametrization.append(fitness_array[ix])
                ix += 1
                continue
            consecutives.append(consecutive_per_parametrization)
            consecutive_per_parametrization = [fitness_array[ix]]
            ix += 1
        consecutives.append(consecutive_per_parametrization)
        # Cast as float in order to get rid of the enforced numpy float np.
        return [float(estimator(consecutive)) for consecutive in consecutives]

    @property
    def averaged_fitness(self):
        """Computes the mean performance averaged per consecutive parametrization
        """
        return self._compute_consecutive_aggregation(np.mean)

    @property
    def min_fitness(self):
        """Computes the mean performance minimized per consecutive parametrization.
        """
        return self._compute_consecutive_aggregation(np.min)

    @property
    def max_fitness(self):
        """Computes the max performance averaged per consecutive parametrization.
        """
        return self._compute_consecutive_aggregation(np.max)

    @property
    def resampled_nbr(self):
        """Computes the number of repetitions per parametrization.
        """
        return self._compute_consecutive_aggregation(len)

    @property
    def measured_noise(self):
        """Computes the standard error associated with each parametrization."""
        noise_measurement = list()
        fitness_array = np.array(self.history["fitness"])
        parameters_array = np.array(self.history["parameters"])
        # If the length is at least one
        if len(fitness_array) > 1:
            # Get the index of the unique parametrization
            # You have to use the index else the array gets sorted and this is problematic
            # for space location dependent heuristics
            for parametrization in np.unique(parameters_array, axis=0):
                noise_measurement.append(
                    float(
                        np.std(
                            fitness_array[
                                np.all(parameters_array == parametrization, axis=1)
                            ]
                        )
                    )
                )
        # Else: there is only 1 parametrization, set average noise to 0
        else:
            noise_measurement = [0]
        return noise_measurement

    @property
    def nbr_iteration_best_fitness(self):
        """Computes the number of iterations required to reach the best fitness"""
        return np.argmin(self.history["fitness"])

    @property
    def fitness_gain_per_iteration(self):
        """
        Computes the fitness gain for each iteration, *i.e.* the shifted fitness vector.

        Returns:
            numpy array: The fitness gain at each iteration
        """
        if self.launched:
            return np.diff(self.history["fitness"])
        print("Fitness gain per iteration can't be computed")
        return None

    @property
    def global_exploration_cost(self):
        """
        Compute the global exploration cost, i.e. the number of times spent in suboptimal states
        (equivalent to the number and the cost of regressions).

        Args:
            fitness: The vector containing the fitness values.

        Returns:
            tuple (int, float): The number of times the algorithm was in a suboptimal zone
                when a better one had already been found, the performance loss due to those
                regressions.
        """
        fitness = self.history["fitness"]
        minimum = fitness[0]
        number_of_states = 0
        performance_cost = 0
        for fit in fitness:
            if fit <= minimum:
                minimum = fit
            else:
                performance_cost += fit - minimum
                number_of_states += 1
        return number_of_states, performance_cost

    @property
    def local_exploration_cost(self):
        """
        Computes the local exploration cost, i.e. the number of times successive operations
        resulted in performance loss (regression) and the total loss due to this difference.

        Returns:
            tuple (int, float): The number of times this phenomena happened, the
                performance loss in fitness
        """
        fitness = self.history["fitness"]
        number_of_states = 0
        performance_cost = 0
        for i in range(len(fitness) - 1):
            # if the algorithm performs worse
            if fitness[i] <= fitness[i + 1]:
                performance_cost += fitness[i + 1] - fitness[i]
                number_of_states += 1
        return number_of_states, performance_cost

    @property
    def size_explored_space(self):
        """
        Given the visited parameters (a.k.a the different states visited by the algorithm) and
        the total numbers of possible states (a.k.a the mutiplication of the length of each
        parameter dimension), computes the percentage of the visited space. Also returns the
        percentage of static moves (= percentage of states that were observed several times) as
        this metric has to be calculated to compute the size of the explored space.

        Returns:
            tuple (float, int): The
                percentage of explored space and the number of duplicated values in the array.
        """
        # Compute space size
        space_size = 1
        for arr in self.parameter_space:
            space_size = space_size * len(arr)
        # Compute the number of unique parameters
        unique_parameters = np.unique(self.history["parameters"], axis=0)
        # Compute the number of different visited coordinates
        percentage_explored_space = len(unique_parameters) / space_size * 100
        # Compute the number of static states
        percentage_static_states = (
            (len(self.history["parameters"]) - len(unique_parameters))
            / len(self.history["parameters"])
            * 100
        )
        return percentage_explored_space, percentage_static_states

    @property
    def total_iteration(self):
        """
        Computes total number of iterations.

        Returns:
            int: the total number of iterations, i.e. initial size + nbr iterations
        """
        return self.initial_sample_size + self.nbr_iteration

    def reset(self):
        """
        Resets the different attributes of the class.
        """
        self.nbr_iteration = 0
        self.elapsed_time = 0
        self.launched = False
        self.history = {
            "fitness": None,
            "parameters": None,
            "truncated": None,
            "resampled": None,
            "initialization": None,
        }

        # resets the heuristic
        self.heuristic.reset()
