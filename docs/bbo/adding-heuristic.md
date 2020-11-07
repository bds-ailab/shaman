# Adding custom heuristics

The programming philosophy behind `bbo` makes it easy to add new heuristics, depending on the users' needs.

## Adding new heuristics

The only requirement to add a new heuristic is to create a class which inherits from the class `Heuristic` and implements three mandatories methods:

!!! warning
    You must keep the same signature for the methods as in the parent class.

* `choose_next_parameter`: uses the previously explored data points to make the next decision.
    * **Function signature**: `self, history, ranges, *args, **kwargs`
    * `history` is a dictionary with four fields, which describes the state of the optimization at each step:
        * `truncated`: list of booleans indicating if the run has been truncated.
        * `initialization`: list of booleans indicating if the run is part of the initialization runs.
        * `resampled`: list of booleans indicating if the run is from a resampled parametrization.
        * `parameters`: list of numpy arrays indicating the tested parameters at this step.
        * `fitness`: list of the fitness values evaluated for the parameters.
    * `ranges` in the discrete set of values (expressed as a numpy array of numpy arrays) that can be taken by the parameters. It is the same as the `parametric_grid` argument of the `BBOptimizer`.

* `summary`: must output a summary of what the heuristic did. Will be printed when the method `summarize` is called.
    * **Function signature**: empty

* `reset`: cleans up the heuristics' attribute
    * **Function signature**: empty

For example, we can create a class `RandomSelector` which selects a value randomly in the parametric grid.

``` python
import numpy as np
from bbo.heuristics.heuristics import Heuristic


class RandomSelector(Heuristic):

    def __init__(self, *args, **kwargs):
        """
        Initialize an object of class RandomSelector that derives from the parent class Heuristic.
        """
        # Initialize parent class
        super(RandomSelector, self).__init__()
        # Count the number of calls to the class
        # (not useful in real life)
        self.selected_values = 0

    def choose_next_parameter(self, history, ranges, *args, **kwargs):
        """
        Randomly select a parametrization from each direction.
        """
        self.selected_values += 1
        return np.array([np.random.choice(axis, 1, replace=True).tolist() for axis in ranges])

    def summary(self, *args, **kwargs):
        """
        Summarize what the heuristic did.
        """
        print(f"{self.selected_values} were tested.")

    def reset(self):
        """
        Resets the heuristic (here does nothing).
        """
```

To use this class with the `BBOptimizer` it must be added as an entry of the `__heuristics__` of the BBOptimizer. The key is the name you want to give the heuristic (that will be used when using `BBOptimizer`) and the value the class representing your heuristic. It must be imported beforehand. It can then be used as the others with the `BBOptimizer` class.

For example, if you want to use the heuristic we just defined, you need to edit the `bbo.optimizer.BBOptimizer` module as such:

``` python
...
# Import the new class
from my_awesome_package import RandomSelector
...

# Add new value to heuristics
    __heuristics__ = {
        "surrogate_model": SurrogateModel,
        "simulated_annealing": SimulatedAnnealing,
        "genetic_algorithm": GeneticAlgorithm,
        "exhaustive_search": ExhaustiveSearch,
        "random_search": RandomSelector
    }
```

## Adding custom methods to existing heuristics

For more details on the development of new functionalities for already existing heuristics, refer to the documentation of the [heuristics](heuristics.md), where the different ways to create custom functions is explained.