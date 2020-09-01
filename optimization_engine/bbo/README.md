# BBO
BBO, which stands for **B**lack-**B**ox-**O**ptimization, is a Python module that
implements different heuristics for finding the optimum of a function with unknown
properties. Two steps are required for such a process:
* Initially sampling the parameter space
* Iteratively select new interesting parameters after analysis of the sampling history.

BBO offers several strategies for sampling the space (Random sampling, Latin Hypercube Sampling) and
for selecting the next parametrization (surrogate modeling, simulated annealing, genetic algorithm ...). It also provides quality assessment and visual
cues to describe the optimization process.

A utility for benchmarking the algorithms on functions with already known optimum is also available
in the package.

## Installation


BBO respects the standard PyPi procedure for installation. In a virtual environment (or not, but this
is bad practice !), run:

```python setup.py install```

And voilà !

## Quickstart

To get started, you first of all need a *black-box*. In this package, it is described as
a Python object that possesses a **compute** method, which returns a float (*fitness value*) when given a numpy array (*parameters*).
This object is given as initialization parameter of an object of class ```BBOptimizer```, along with
the type of *initialization* and *heuristic* you want to use, along with their specific parameters. For example,
let's say I want to optimize the parabola function. I first have to define and instanciate an object of class ```Parabola```.

```python
class Parabola:
    def __init__(self):
        print("I'm the Parabola function ! Good luck finding my optimum !")

    def compute(self, array_2d):
        return array_2d[0] ** 2 + array_2d[1] ** 2

parabola = Parabola()
```

If I then decide I want to optimize this function on a 2 by 100 grid centered on 0 using *surrogate modeling*, with an initialization sample
of size 10 using *Latin Hypercube Sampling* and using a *gaussian process regressor* to perform regression and *maximum improvement* to perform next parameter acquisition, with a maximum number of iterations of 10 steps,
I can use the ```BBOptimizer``` in the following way:

```python
from bbo.heuristics.surrogate_models.next_parameter_strategies import expected_improvement
from sklearn.gaussian_process import GaussianProcessRegressor

bb_obj = BBOptimizer(black_box=parabola,
                     parameter_space=np.array([np.arange(-101, 100, 1), np.arange(-100, 100, 1)).T,
                     heuristic="surrogate_model",
                     regression_model=GaussianProcessRegressor,
                     next_parameter_strategy=expected_improvement,
                     initial_sample_size=10,
                     initial_draw_method="latin_hypercube_sampling",
                     max_iteration=10)
bb_obj.optimize()
```



For a more in depth description of the package and how to use its functionalities,
the reader is strongly recommended to read the documentation and the different Jupyter [notebooks](notebooks)
that describe some of the most common use cases.

## Further information
The reader interested in the theoretical foundation and review of this package is
advised to go look into the [notebooks](notebooks) folder for extensive documentation
of the package and its heuristics.

Stay tuned for a report that will summarize both the methodology and the
benchmarking results on different theoretical and real curves.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute and help the BBO package grow !

## Future of BBO

The main milestone of BBO's life will be its integration with the ```experiment_design```
package, in order to give birth to the ```SHAMan``` utility, that will perform real-time application
optimization.

## About the author

This module has been developed in the context of my PhD thesis on the auto-tuning of HPC applications here at Atos-Bull, within the BDS Data Management Team overseen by Philippe Couvée,
under the supervision of Gaël Goret and Soraya Zertal. Please feel free to contact me @ [sophie.robert@atos.net](sophie.robert@atos.net) if you want
to discuss anything black-box optimization related (or, more generally, auto-tuning of applications).
