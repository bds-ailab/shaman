# Black-box optimization

SHAMan comes with a stand-alone Python library called `bbo` that can be used directly in an interactive Python session. `bbo` is a generic modular library to perform black-box optimization of Python object.

## What is black-box optimization ?

Black-box optimization refers to the optimization of a function of unknown properties, most of the time costly to evaluate, which entails a limited number of possible evaluations. The goal of the procedure is to find the optimum of a function f in a minimum of evaluations without making any hypothesis on the function.

$$
\text{Find}\ \{x_i\}_{1 \leq i \leq n} \in \Theta\ \text{s.t.}\ |min(\{f(x_i)\}_{1 \leq i \leq n}) - min(f) \le \epsilon|$$

by denoting:

-   $f$ the function to optimize (black-box)

-   $\Theta$ the parameter space

-   $\epsilon$ a convergence criterion between the found and the estimated minimum

The search can be divided in two steps:

1. **Initialization step**: it consists in sampling the parametric space in order to evaluate the performance of several well chosen starting points by using an initialization strategy.

2. **Feedback step**: it consists in iteratively selecting a parametrization, evaluating the black-box function at this point and selecting accordingly the next data point to evaluate by using a heuristic.

## Available heuristics

`bbo` comes with three of the most well-known black-box optimization heuristics, because of their simplicity of implementation and their proven efficiency in several fields:

- **Genetic algorithms**: they consist in selecting a subset of parameters, among the already tested parametrizations, according to a selection mechanism that considers the objective value of each parametrization.
- **Surrogate models**: Surrogate modeling consists in using a regression or interpolation technique over the currently known surface to build a computationally cheap approximation of the black-box function and to then select the most promising data point in terms of performance on this surrogate function by using an acquisition function. Any regression or interpolation function can be used to build the surrogate model.
- **Simulated annealing**: the simulated annealing heuristic is a hill-climbing algorithm which can probabilistically accept a solution worse than the current one. The algorithm is started using an initial “temperature” value, which will decrease over time. Then, at each iteration, the algorithm randomly selects a parametrization neighboring the current one and computes its execution time. If the new parametrization is better than the current parametrization, it is automatically accepted. If not, a probability of acceptance is computed as a function of the system's temperature. The temperature of the system then decreases, according to a cooling schedule which ensures that the probability of accepting a solution worse than the current one lowers at each iteration until it draws to zero at the end of the algorithm. 

More details on the different heuristics and how to use them with `bbo`are available [here](heuristics.md).

As there are many possible state-of-art heuristics, `bbo` relies on plugins to make it easy to add new heuristics or new hyperparameters to existing heuristics, as is explained in [here](adding-heuristic.md).

## Install

SHAMan is bundled using the package manager [Poetry](https://python-poetry.org/). To install `bbo` in stand-alone mode, you can run at the top of the SHAMan folder:
```
poetry install -e bbo
```

To make sure the package is properly installed, you can call in an interactive Python session:

```
import bbo
```

## Main principle

A function to optimize is the only requisite for black-box optimization. For `bbo`, a black-box function is a **Python object with a method compute**, which takes as input a **numpy array** and **returns a scalar**. If you’d like to perform an operation on the output of the compute method, you can specify a special value for the argument **perf_function** of the BBOptimizer object.

## Example

In this example, we will optimize the [Ackley function](https://en.wikipedia.org/wiki/Ackley_function#:~:text=In%20mathematical%20optimization%2C%20the%20Ackley,in%20his%201987%20PhD%20Dissertation.). We will begin by making the right imports:

``` python
import numpy as np
from bbo.optimizer import BBOptimizer
```

We then define a class `FakeBlackBox`, which has a `compute` method corresponding to the value returned by the [Ackley function](https://en.wikipedia.org/wiki/Ackley_function#:~:text=In%20mathematical%20optimization%2C%20the%20Ackley,in%20his%201987%20PhD%20Dissertation.).

``` python
class FakeBlackBox:
    def __init__(self):
        print("I'm the Ackley function ! Good luck finding my optimum !")
        
    def compute(self, array_2d):
        return -20 * np.exp(-0.2 * np.sqrt(0.5 * (array_2d[0]**2 + array_2d[1]**2))) - np.exp(0.5 * (np.cos(2 * np.pi * array_2d[0]) + np.cos(2 * np.pi * array_2d[1]))) + np.exp(1) + 20
```

In this example, we'll arbitrarily decide to work with **surrogate models**, using **expected improvement** as an acquisition function. You can learn more about surrogate models by clicking on this [here](heuristics.md).

``` python
# As you'll soon learn from the tutorial on surrogate modeling, any regression function available in sklearn can be used with surrogate modeling
from sklearn.gaussian_process import GaussianProcessRegressor
# Import the expected_improvement function
from bbo.heuristics.surrogate_models.next_parameter_strategies import expected_improvement
```

Once all the imports are done, an object of class `FakeBlackBox` can be created, along with the parametric space on which we want to optimize it. Note that in `bbo`, **the parametric space must be discrete**. We'll look for the minimum of the Ackley function on $[-10, 10]\times[-5, 5]$. The parametric space must be described as an array of numpy arrays, each array representing the possible values for each dimension.

``` python
# create the fake_black_box object
fake_black_box = FakeBlackBox()
# choose the optimization grid
parametric_grid = np.array([np.arange(-10, 10, 1), np.arange(-5, 5, 1)]).T
```

The optimization process is made by an object of class `BBOptimizer`. This class is the common interface for all of the heuristics: after specifiying the wanted heuristic *via* the argument `heuristic`,the specificity of each heuristic is passed as an argument upon the initialization of this object.

``` python
 # Parametrize the BlackBox optimizer as you need
bb_obj = BBOptimizer(black_box = fake_black_box, # the black-box to optimize
                     parameter_space = parametric_grid, # the grid on which to perform the optimization
                     initial_sample_size=3, # the initial size of the sample
                     initial_draw_method="uniform_random", # the method to use to draw the parameters
                     heuristic="surrogate_model", # the name of the heuristics to use
                     max_iteration=10, # the maximum number of iterations
                     # the following arguments are specific to surrogate modeling:
                     regression_model=GaussianProcessRegressor, # the regression function
                     next_parameter_strategy=expected_improvement) # the acquisition function
```

Once the `BBOptimizer` has been parametrized as wanted, the optimization process can begin. By calling the `optimize` method of the optimizer, the optimization process can begin and the function returns the optimal parameters found by the optimizer.

``` python
bb_obj.optimize()
```

The `summarize` method gives us different global information on the optimization process, such as the total number of iterations, the elapsed time, the fitness evaluation, the number of evaluations ... It also provides heuristic specific information: in the case of the surrogate models, the RMSE of the regression algorithm at the end.

``` python
bb_obj.summarize()
```

More complete examples for each heuristic are available [here](heuristics.md)