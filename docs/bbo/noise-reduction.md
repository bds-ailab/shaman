# Noise reduction

## Why is noise reduction required ?

Because of their highly dynamic nature and the complexity of applications and software stacks, HPC systems are subjected to many interference when running in production, which results in a different performance measure for each run even with the same system's parametrization. If this variability is not taken into account, the efficiency of black-box heuristics can be significantly reduced because of a slow down of the optimization process. In a **low-noise setting** (for example if you know you won't share resources with several users), noise reduction strategies are irrelevant because they can waste computing resources (by retrying already tried parametrization), but in a **high-noise setting**, noise reduction methods are **critical to ensure the quality of the solution suggested by the optimizer**.

The problem solved by the optimizer can be described by the search of a performance function that can only be accessed through its observations that are tainted with noise.

$$min \mathbb{E}(F(x)),\ x \in \mathcal{P} ||
F(x) = f(x) + \epsilon(x)$$

with $f(x)$ representing the "true" execution time for parametrization $x$, while we only have access to the "observed" or "sampled" execution times $F(x)$. The noise, which can depend on the parametrization, is a function of $x$ and is represented by $\epsilon(x)$. We treat the execution time as a random variable which realization are the elapsed times for each run.

## Available resampling method

To deal with the possible noise introduced when measuring the performance of the application, you can add to `bbo` a resampling component, which re-evaluates several times the same parametrization in order to have a more precise idea of the performance value for this parametrization. Two different types of resampling are available.

### Aggregation functions

To perform resampling, an aggregation function is necessary to be selected so that the decisions made by the optimizer can be based on an aggregated performance function. Two available aggregation methods are the `mean` and the `median`. The aggregation method is given to the class `BBOptimizer` using the `fitness_aggregation` argument. It can take as value **any Python function** to compute an aggregation. If this value is not specified, the default behavior of `bbo` is to use the mean as aggregator of the fitness values within the same parametrization.

By defining a black-box like in the introduction section,

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

we can use the median as a custom aggregation function:

``` python hl_lines="11 12"
from bbo.optimizer import BBOptimizer
import numpy
from bbo.heuristics.surrogate_models.next_parameter_strategies import expected_improvement
from sklearn.gaussian_process import GaussianProcessRegressor


bb_obj = BBOptimizer(
    black_box=fake_black_box,
    heuristic="surrogate_model",
    max_iteration=20,
    initial_sample_size=2,
    parameter_space=parameter_grid,
    next_parameter_strategy=expected_improvement,
    regression_model=GaussianProcessRegressor,
    resampling_policy="simple_resampling",
    nbr_resamples=2,
    fitness_aggregation="simple_fitness_aggregation",
    estimator=numpy.median,
)
```

### Static resampling

Static resampling consists in **repeating each parametrization a fixed number of times**. It is activated using the `resampling_policy` argument of the `BBOptimizer` class. It requires to also give a value for the argument `nbr_resamples` (which will correspond to the number of resamples). You can add custom fitness aggregation (like seen in the above section) or just use the default behavior of using the mean.

``` python hl_lines="15 16"
from bbo.optimizer import BBOptimizer
import numpy
from bbo.heuristics.surrogate_models.next_parameter_strategies import expected_improvement
from sklearn.gaussian_process import GaussianProcessRegressor


bb_obj = BBOptimizer(
    black_box=fake_black_box,
    heuristic="surrogate_model",
    max_iteration=20,
    initial_sample_size=2,
    parameter_space=parameter_grid,
    next_parameter_strategy=expected_improvement,
    regression_model=GaussianProcessRegressor,
    resampling_policy="simple_resampling",
    nbr_resamples=5,
)
```

### Dynamic resampling

Dynamic resampling consists in **resampling a parametrization until the 95% confidence interval around the mean decreases to a certain width**, selected by the user as percentage of the mean around this point. This method is more flexible than static resampling, as it adapts to the noise present on the machine at this time. When measured at a time when the system is particularly noisy, the parametrization is repeated many times and when the system is idle, the parametrization is repeated less. To use dynamic resampling with `bbo`, you need to set the argument `resampling_strategy` to `dynamic_resampling` and `percentage` to define the width of the confidence interval as a function of the mean.

In the example below, resampling happens until the width of the 95% confidence interval falls below 10% of the mean of the fitness value measured at this point.

``` python hl_lines="15 16"
from bbo.optimizer import BBOptimizer
import numpy
from bbo.heuristics.surrogate_models.next_parameter_strategies import expected_improvement
from sklearn.gaussian_process import GaussianProcessRegressor


bb_obj = BBOptimizer(
    black_box=fake_black_box,
    heuristic="surrogate_model",
    max_iteration=20,
    initial_sample_size=2,
    parameter_space=parameter_grid,
    next_parameter_strategy=expected_improvement,
    regression_model=GaussianProcessRegressor,
    resampling_policy="dynamic_resampling",
    percentage=0.1,
)
```