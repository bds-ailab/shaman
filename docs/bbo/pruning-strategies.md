# Pruning strategies

Pruning strategies consist in stopping on-going runs, when a parametrization is **considered to be unpromising** (*i.e.* it does not satisfy a certain performance criteria).

To use pruning strateges, the `async_optim` argument of the `BBOptimizer` class should be set to `True`. You should also specify a `max_step_cost` value, which tells the optimizer to stop any run which performance goes above this threshold. By default, the considered performance criterion is the **elapsed time** of the black box computation, but more complex criteria can be used by adding a method `step_cost_function` to the class used as the black-box. It is also possible to add a `on_interrupt` method to the black-box class, which performs an action once the run has been interrupted.

For example, we can add an `on_interrupt` methods to an example black-box class. This class computes the value of the Ackley function, and then performs a sleep of this length (this is a dummy example, I am not sure why someone would use this in real-life ...). When a run is being interrupted because of poor performance (in this case the elapsed time), it will print `"I have been interrupted."`.

``` python
import numpy as np
import time


class AsyncFakeBlackBox:
    def __init__(self):
        print("I am a demo class for asynchronous optimization.")
        
    def compute(self, array_2d):
        score = -20 * np.exp(-0.2 * np.sqrt(0.5 * (array_2d[0]**2 + array_2d[1]**2))) - np.exp(0.5 * (np.cos(2 * np.pi * array_2d[0]) + np.cos(2 * np.pi * array_2d[1]))) + np.exp(1) + 20
        time.sleep(score)
        return score

    def on_interrupt(self):
        print("I have been interrupted.")


# create the fake_black_box object
async_fake_black_box = FakeBlackBox()
# choose the optimization grid
parametric_grid = np.array([np.arange(-10, 10, 1), np.arange(-5, 5, 1)]).T
```

When setting up the `BBOptimizer` like in the example below, all runs that run longer than 20 seconds (the value for the `max_step_cost`) will be interrupted. It will also print `"I have been interrupted."` for each of these runs.

``` python hl_lines="17"
from bbo.optimizer import BBOptimizer
import numpy
from bbo.heuristics.surrogate_models.next_parameter_strategies import expected_improvement
from sklearn.gaussian_process import GaussianProcessRegressor


bb_obj = BBOptimizer(
    black_box=async_fake_black_box,
    heuristic="surrogate_model",
    max_iteration=20,
    initial_sample_size=2,
    parameter_space=parameteric_grid,
    next_parameter_strategy=expected_improvement,
    regression_model=GaussianProcessRegressor,
    async_optim=True
)
```

Adding a custom `step_cost_function` allows to use external values to check if a run should be interrupted. In the case of SHAMan, for the optimization of HPC systems, it consists in using a function which interrogates the Slurm manager to check the time elapsed time of the application.