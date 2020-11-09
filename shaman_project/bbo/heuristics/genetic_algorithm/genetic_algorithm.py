"""Implementation of the genetic algorithm as an heuristic for black-box
optimization."""

# Ignore unused argument kwargs
# pylint: disable=unused-argument

import numpy as np

from bbo.heuristics.heuristics import Heuristic


class GeneticAlgorithm(Heuristic):
    """Object that will perform the genetic algorithm.

    Inherits from the mother class Heuristic.
    """

    def __init__(
        self,
        selection_method,
        crossover_method,
        mutation_method,
        mutation_rate,
        *args,
        max_repeat=5,
        **kwargs,
    ):
        """Initializes a GeneticAlgorithm object.

        Args:
            selection_method (Python function): The method to use in order
                to select the two parents chromosomes.
            crossover_method (Python function): The method to use to mate
                the parents and cross their alleles.
            mutation_method (Python function): The method to use to perform
                a mutation on a given chromosome.
            mutation_rate (float): A float between 0 and 1 to determine the
                probability of mutation at each round.
            max_repeat (int): The maximum of repetitions allowed when looking
                for a new child *args, **kwargs: The arguments for the
                selection of the fittest parent.
        """
        # Initialization of the mother class
        super(GeneticAlgorithm, self).__init__(
            selection_method, crossover_method, mutation_method
        )
        # save selection method
        self.selection_method = selection_method
        # save crossover method
        self.crossover_method = crossover_method
        # save mutation method
        self.mutation_method = mutation_method
        # save mutation rate
        self.mutation_rate = mutation_rate
        # set number of mutation to 0
        self.nbr_mutation = 0
        # save maximum repetition to find new offspring
        self.max_repeat = max_repeat
        # save as a list of tuples the parents and their offspring,
        # using the (parent_1, parent_2, offspring) notation
        self.family_line = list()
        # save args and kwargs
        self.args = args
        self.kwargs = kwargs

    def choose_next_parameter(self, history, ranges, *args, **kwargs):
        """Select the next parameters for the optimization process, in this
        case the children of the two parents selected as the fittest.

        A genetic algorithm has the following rule for choosing the
        next parameter:
            1) Use a selection method to pick two parents fit for mating
            2) Use a crossover method to mate those two parents
            3) Probabilistically determine whether or not the mutation method
            should be applied.

        Args:
            history (dict): the history of the optimization, i.e. the tested
                parameters and the associated value.
            ranges (numpy array of numpy arrays): the possible values of each
                parameter dimension.

        Returns:
            numpy array: The next parameter, i.e. the child born from the
                reproduction of the two parents.
        """
        idx = 0
        # loop until the child is different from its two parents
        while True and idx < self.max_repeat:
            # Select two parents using the selection method
            parent_1, parent_2 = self.selection_method(
                history=history, *self.args, **self.kwargs
            )
            # Mate those two parents to compute a new child
            child = self.crossover_method(parent_1, parent_2)
            # Is there a mutation at this round? Compute the probability
            # using a bernouilli random
            # variable
            mutation = np.random.binomial(1, self.mutation_rate)
            # If so, perform mutation on the child and return the mutant form
            if mutation:
                child = self.mutation_method(child, ranges)
                self.nbr_mutation += 1
            if not np.array_equal(child, parent_1) and not np.array_equal(
                child, parent_2
            ):
                break
            idx += 1
        self.family_line.append((parent_1, parent_2, child))
        return child

    def summary(self, *args, **kwargs):
        """Returns a summary of the optimization process of the genetic
        algorithm:

        - A description of the 'family line', using the format:
            (parent_1, parent_2, child)
        - The number of mutations
        """
        print(f"Number of mutations: {self.nbr_mutation}")
        # graphical representation of the family tree
        print("Family tree:")
        for family in self.family_line:
            print(f"{family[0]} + {family[1]}")
            print(f"|_> {family[2]}")

    def reset(self):
        """Resets the algorithm."""
