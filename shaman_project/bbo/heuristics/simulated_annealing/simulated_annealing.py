"""This modules implements the simulated annealing heuristic, which is a hill-
climbing algorithm which can probabilistically accept a worse solution than the
current one. The probability of accepting a value worse than the current one
decreases with the number of iterations: this introduces the notion of the
system's "temperature" (hence the analogy of metal's annealing). The
temperature is a value that decreases overtime according to a cooling schedule
which defines the temperature decrease per iteration. As the temperature lower,
the probability of moving upward (i.e. accepting a worse solution) decreases
until it reaches 0 and the system does not move anymore.

As with all hill-climbing algorithm, there is the necessity of defining a
point "neighborhood" by using some distance in order to select the next
candidate for evaluation.

Also, the simulated annealing heuristic comes with the possibility of
restarting the system, i.e. setting the temperature back to its maximum value.
There are many ways of restarting the system and we have selected two of them:
random restarts, which restart the system following a Bernouilli law
(whose parameter can be tuned) and energy threshold restarts which
heat the system up once the system's energy is under a certain threshold.
"""

# Ignore unused argument kwargs
# pylint: disable=unused-argument

import numpy as np
from numpy.random import uniform

from bbo.heuristics.heuristics import Heuristic


class SimulatedAnnealing(Heuristic):
    """Object that will perform the simulated annealing. As all heuristics, it
    derives from the mother class Heuristic.

    The simulated annealing heuristic, which is a hill-climbing algorithm
    which can probabilistically accept a worse solution than the current one.
    The probability of accepting a value worse than the current one decreases
    with the number of iterations: this introduces the notion of the system's
    "temperature" (hence the analogy of metal's annealing).
    The temperature is a value that decreases overtime according to a cooling
    schedule which defines the temperature decrease per iteration.
    As the temperature lower, the probability of moving upward (i.e. accepting
    a worse solution) decreases until it reaches 0 and the system does not
    move anymore.

    As with all hill-climbing algorithm, there is the necessity of defining
    a point "neighborhood" by using some distance in order to select the
    next candidate for evaluation.

    Also, the simulated annealing heuristic comes with the possibility of
    restarting the system, i.e. setting the temperature back to its maximum
    value. There are many ways of restarting the system and we have selected
    two of them: random restarts, which restart the system following a
    Bernouilli law (whose parameter can be tuned) and energy threshold
    restarts which heat the system up once the system's energy is under
    a certain threshold.
    """

    def __init__(
        self,
        initial_temperature,
        neighbor_function,
        cooldown_function,
        *args,
        restart=False,
        max_restart=5,
        **kwargs,
    ):
        """Initializes a SimulatedAnnealing object with different parameters.

        Args:
            initial_temperature (float): the temperature at the start of
                the algorithm.

            neighbor_function (function): how the neighbours should be
                selected.

            cooldown_function (function): how the model's temperature should
                cool down.

            restart (bool or function): If restart should not be enabled,
                defaults to false, else, the function to use for restarting
                the system and finding out the next temperature.

            max_restart (int): The maximum values of restarts.
        """
        super(SimulatedAnnealing, self).__init__(
            initial_temperature, neighbor_function, cooldown_function
        )

        # check that the maximum temperature is a float or an int
        if not isinstance(initial_temperature, (int, float)):
            raise TypeError(
                "Initial temperature should either be an int or a float. "
                f"{initial_temperature} "
                "is not a valid value."
            )

        if initial_temperature < 0:
            raise TypeError("Temperature can't be negative.")
        # save maximum temperature as initial value
        self.t_max = initial_temperature
        # set current temperature to the maximum value
        self.current_t = self.t_max

        # Save neighbor and cooldown schedules
        self.neighbor_function = neighbor_function
        self.cooldown_function = cooldown_function

        # number of times the algorithm has run in order to compute
        # the value of the temperature
        # at each iteration
        self.nbr_iteration = 0

        # store the restart type in an attribute
        self.restart = restart
        # if restart is enabled
        if restart:
            # store the number of restarts in an attribute
            self.nbr_restart = 0
            # store the maximum number of possible restarts
            self.max_restart = max_restart
            # store the method used for restart
            self.restart_function = restart
        else:
            # signal to the user that all parameters will be ignored.
            print(
                "Restart has been disabled, values for the number of restart"
                "will be ignored."
            )
        # will contain the list of the values of the system's probability of
        # acceptance
        self.energy = list()
        # will contain the list of the values for the energy
        self.temperature = list()
        # contains the various arguments for the restart methods
        self.args = args
        self.kwargs = kwargs

    def choose_next_parameter(
        self, history, ranges, current_parameters=None, *args, **kwargs
    ):
        """Selects the next parameter using the simulated annealing heuristic
        workflow:

            Select a neighboring point using the neighbor_function

            Evaluate the fitness of this point

            If the new point fitness is better than the current fitness,
                select this point.

            Else, compute the acceptance probability using the
                Metropolis-Hastings formula, as a function of the
                system's temperature.

                Draw a float between 0 and 1 using a random uniform
                distribution.

                If this float is lower than the acceptance probability,
                accept the new "worse" parameter

            Start again until the temperature drops below 0.01 OR the stopping
            criteria from the optimizer are met.


        If restart is enabled, determine at each iteration if the system
        should be restarted.


        Args:
            history (dict): A python dictionary of the form
                that contains the previous evaluations of the black-box
                function.
            ranges (numpy array of arrays): The parametric space to explore.
            current_parameters (numpy array): The parameter to start the
                optimization process on.
                It must have been already evaluated by the algorithm.
                If no value is specified, set it to the last evaluated
                parameter in the history.

        Returns:
            Numpy array: The next parameters to evaluate.
        """
        # add to list of temperature
        self.temperature.append(self.current_t)
        # compute current temperature
        self.current_t = self.cooldown_function(
            initial_temperature=self.t_max,
            current_iteration=self.nbr_iteration,
            *self.args,
            **self.kwargs,
        )
        # if the temperature is below 0.01, break
        if self.current_t <= 0.01:
            self.stop = True

        if current_parameters is None:
            # the current parameter as taken from the history parameters two
            # steps back
            current_parameters = history["parameters"][-2]
            # the current fitness value as taken from the history fitness two
            # steps back
            current_fitness = history["fitness"][-2]
        else:
            # The current fitness is taken from matching the fitness
            current_fitness = history["fitness"][
                np.equal(history["parameters"], current_parameters).all(axis=1)
            ]
        # the next parameters as taken from the history
        # parameters one step back
        next_parameter = history["parameters"][-1]
        # the next fitness value as taken from the history fitness two steps
        # back
        next_fitness = history["fitness"][-1]

        # compute the probability of acceptance
        probability_of_acceptance = np.exp(
            (current_fitness - next_fitness) / self.current_t
        )

        # if the next fitness is better than the current one:
        # repeat process using next parameter
        if current_fitness >= next_fitness:
            chosen_parameter = self.neighbor_function(next_parameter, ranges)
            self.energy.append(0)
        # else, keep the possibility of 'climbing-up' the hill by computing a
        else:
            self.energy.append(probability_of_acceptance)
            # draw a random value between 0 and 1
            threshold = uniform(0, 1)
            if threshold < probability_of_acceptance:
                chosen_parameter = self.neighbor_function(
                    next_parameter, ranges)
            else:
                # else go back to initial value
                chosen_parameter = current_parameters
        # Add +1 to number of iterations
        self.nbr_iteration += 1

        # Check if the restart option has been enabled
        if self.restart and self.nbr_restart < self.max_restart:
            restart_flag, new_temperature = self.restart_function(
                current_probability=probability_of_acceptance,
                initial_temperature=self.t_max,
                current_iteration=self.nbr_iteration,
                *self.args,
                **self.kwargs,
            )

            if restart_flag:
                self.current_t = new_temperature
                chosen_parameter = history["parameters"][np.argmin(
                    history["fitness"])]
                self.nbr_restart += 1
        # return the parameter for evaluation
        return chosen_parameter.flatten()

    def summary(self, *args, **kwargs):
        """Summary for the simulated annealing:

            - Number of restarts

        Returns:
            Outputs summary to screen.
        """
        if self.restart:
            print(f"Number of restarts: {self.nbr_restart}")

    def reset(self):
        """Resets the system by reseting the attributes to their original
        value."""
        self.current_t = self.t_max
        self.nbr_iteration = 0
        if self.restart:
            self.restart = 0
        self.energy = list()
