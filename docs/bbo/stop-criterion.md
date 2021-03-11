# Stop criterion

When running the optimization algorithm, the easiest stop criterion is based either on a budget of possible steps (also called exhaustion based) or on a time-out based on the maximum elapsed time for the algorithm: once the budget has been spent, the algorithm stops and returns the best found parametrization. This is the default behavior of `bbo` and by extension `SHAMan`. However,this criterion can be inefficient, as it has no adaptive quality on the tuned system. That's why SHAMan implements three other types of stop criteria to improve the convergence performance.

# Improvement based criterion

Improvement based criteria consist in stopping the optimization process if it does not bring any improvement over a given number of iterations. Depending on the wanted behavior, the improvement can either be measured globally as the average of the evaluated values or locally as the change in optimum values. In `bbo` the improvement is defined as the ratio of different between the value of a statistical estimator on the last iterations, when compared to the values without these iterations. If this improvement ratio does not go above a threshold set by the user, the optimization process stops. Any estimator can be used, but recommended estimators are the mean, the median or the minimum. To use improvement based criterion, the syntax is as follow to use in-memory. Note that to use stop criterion with SHAMan through the command line, the syntax is similar.

We begin by defining a black-box object to optimize.

``` python
import numpy as np


class FakeBlackBox:
    def __init__(self):
        print("I'm the Ackley function ! Good luck finding my optimum !")
        
    def compute(self, array_2d):
        return -20 * np.exp(-0.2 * np.sqrt(0.5 * (array_2d[0]**2 + array_2d[1]**2))) - np.exp(0.5 * (np.cos(2 * np.pi * array_2d[0]) + np.cos(2 * np.pi * array_2d[1]))) + np.exp(1) + 20

# create the fake_black_box object
fake_black_box = FakeBlackBox()
# choose the optimization grid
parametric_grid = np.array([np.arange(-10, 10, 1), np.arange(-5, 5, 1)]).T
```

we can use the minimum as the improvement estimator, the window of iterations to compute the estimator on to 5, and set the improvement threshold to 0.1: the optimization process stops if the minimum found over the 5 last iterations isn't at least 5% better than the rest of the trajectory.

``` python hl_lines="15 16 17 18"
from bbo.optimizer import BBOptimizer
import numpy
from bbo.heuristics.surrogate_models.next_parameter_strategies import expected_improvement
from sklearn.gaussian_process import GaussianProcessRegressor


bb_obj = BBOptimizer(
    black_box=fake_black_box,
    heuristic="surrogate_model",
    max_iteration=50,
    initial_sample_size=2,
    parameter_space=parameter_space,
    next_parameter_strategy=expected_improvement,
    regression_model=GaussianProcessRegressor,
    stop_criterion="improvement_criterion",
    stop_window=5,
    improvement_estimator=min,
    improvement_threshold=0.1
)
bb_obj.optimize()
```

# Movement based criteria

Movement based criteria consider the movement of the parametric grid as a criteria to stop the optimization. Two types of the criteria are available in `bbo`: a count based on distinct parametrization and a distance based stop criterion. 

## Number of distinct parametrization

The optimization algorithm stops once there is less than a certain number of distinct parametrization evaluated over the last n iterations. For example, here, we parametrize the optimizer to stop the optimization process once there is less than 5 distinct parametrization in the last 10 optimization steps.

``` python hl_lines="15 16 17"
from bbo.optimizer import BBOptimizer
import numpy
from bbo.heuristics.surrogate_models.next_parameter_strategies import expected_improvement
from sklearn.gaussian_process import GaussianProcessRegressor


bb_obj = BBOptimizer(
    black_box=fake_black_box,
    heuristic="surrogate_model",
    max_iteration=50,
    initial_sample_size=2,
    parameter_space=parameter_space,
    next_parameter_strategy=expected_improvement,
    regression_model=GaussianProcessRegressor,
    stop_criterion="count_movement",
    stop_window=10,
    nbr_parametriaztion=5
)
bb_obj.optimize()
```

## Distance measured over the parametric grid

The optimization algorithm stops once the average euclidean distance among the last n iterations falls below a set threshold (i.e. the last tested parametrization are not very far apart). For example, we parametrize here the optimizer to stop the optimization process once the average distance between the last 5 iterations is below 0.5.

``` python hl_lines="15 16 17"
from bbo.optimizer import BBOptimizer
import numpy
from bbo.heuristics.surrogate_models.next_parameter_strategies import expected_improvement
from sklearn.gaussian_process import GaussianProcessRegressor


bb_obj = BBOptimizer(
    black_box=fake_black_box,
    heuristic="surrogate_model",
    max_iteration=50,
    initial_sample_size=2,
    parameter_space=parameter_space,
    next_parameter_strategy=expected_improvement,
    regression_model=GaussianProcessRegressor,
    stop_criterion="distance_movement",
    stop_window=5,
    distance=0.5
)
bb_obj.optimize()
```
