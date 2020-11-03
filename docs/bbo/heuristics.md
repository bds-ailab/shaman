# Available heuristics

## Surrogate models

The principle of surrogate modeling is to find a computationally cheap to evaluate function that describes well the unknown function, and decide which parameter should be evaluated next given by exploiting the properties of this regressed curve.

### Main principles

The main idea behind surrogate modeling is to use a regression or interpolation technique over the currently known surface to build the surrogate and to then select the most promising data point in terms of performance gain using this surrogate function.

According to this definition, surrogate modeling requires:

* A regression or interpolation function regressor

* A procedure to select the next potentially interesting point given a surrogate acquisition_function

If given a budget of `n` iteration, `S` and `F` being respectively the parameters and the value of the function on these parameters, the algorithm can be described as follow:

``` python
ix = 0
while ix < N:
    surrogate_model = regressor(S, F)
    next_data_point = acquisition_function(surrogate_model)
    S.append(next_data_point)
    F.append(f(next_data_point))
    ix += 1
```
### Regressing the curve

As can be seen from the definition above, the first required step is to regress or interpolate the already existing data point. Any regression or interpolation function can be used to build the surrogate, as long as it provides a computationally cheap approximation of the black-box function. In our case, any regression function that possess a `fit` and `predict` method can be used, which means that any regression function from the `sklearn` package can be used.

However, some acquisitions functions require some of the information yielded by specific regression techniques, and they thus can't all be used interchangeably. It is for example the case with maximum probability of improvement and expected improvement, as we will see later: those functions require the statistical assumptions made by Kriging regression and can't be used without it. In terms of development, if you want to use maximum probability of improvement or expected improvement as acquisition function, you will have to use a function which `predict` method returns both the value of the prediction and its standard error.

### Next parameter strategies

Given the surrogate model, an acquisition function should be able to find the most promising data point. Three strategies are implemented in `BBO`. We discuss below the different strategies.

However, because of the modular philosophy of `bbo`, you can create your own acquisition function and use it along with the surrogate heuristics.

#### Using the minimum as acquisition function

The simplest method is to use the surrogate as the cost function and select its optimum. This method has the advantage of not making any statistical assumption on the black box function. Any minimization algorithm can be used to find this minimum. In BBO, two methods are available:

* L-BFGS minimizer
* CMA minimizer

For example, to import the CMA minimizer, you would write:
```
from bbo.heuristics.surrogate_models.next_parameter_strategies import CMA_optimizer
```

#### Maximum probability improvement

In this case, the acquisition function is the probability that the $f$ value for the next point will be lower than the current best value $f^*$, *i.e.* computing $\mathbb{P}(f(x) \leq f ^*)$.
					
Under the assumption that the black-box function can be accurately described by a probabilistic process (which means that you have to use a class which `predict` method returns the average value and its standard error, like sklearn's <code>GaussianProcessRegressor</code>), the estimated mean and standard error for parameter $x$ $\mu(x)$ and $\sigma(x)$ is available. We can derive that:
					
					
$$\mathbb{P}(f(x) \leq f ^*) = \Phi(\frac{f^* - \hat{\mu}(x)}{\hat{\sigma}(x)}) $$

$\Phi$ being the normal cumulative function.
					
This method encodes whether or not we might get a reward, but does not take its potential value into account. As the search region under a given parameter $x$ becomes more and more known, $\sigma(x)$ gets smaller and so does $MPI(x)$. The algorithm then switches to a different search region.

You can import it by using:
``` python
from bbo.heuristics.surrogate_models.next_parameter_strategies import maximum_probability_improvement
```

The version implemented in `bbo` computes the $MPI$ for every data point and then uses brute force minimization to select the point with the highest score.

#### Expected improvement

This method both encodes exploration (exploring spaces with a high variance) and exploitation (exploring spaces with a low mean). Not only it takes into account whether or not the next point will induce a smaller value for $f$ but it also considers the gain from the switch. Unlike $MPI$ which only looks for a smaller value, $EI$ takes into account the difference between the old and the new data point.
					
For each point of the parametric space, we can define the improvement as:
					
$$I(x) =\begin{cases} f^* - f(x) & f(x) < f^* \\
0 &  f(x) \geq 0
\end{cases}$$

Which can also be written as $I(x) = max(f^*- f(x), 0)$. In the case that $f$ is approximated by a Gaussian process, $I$ is a random variable and its expectation over each possible data point can be computed. To simplify the equations below, we will denote $\mu(x)$ by $\mu$ and $\sigma(x)$ as $\sigma$ when there is no possible doubt. We can re-parametrize the process $f(x)$ as $f(x) \sim \mu(x) + \sigma(x) \times \epsilon$ where $\epsilon \sim \mathcal{N}(0,1)$.
					
$$
\begin{align}
EI(x) 
& = \mathbb{E}(I(x))  \\
& = \int_{-\infty}^{\frac{f^* - \mu}{\sigma}} I(x) \phi(u) du  \\
& = \int_{-\infty}^{\frac{f^* - \mu}{\sigma}}  (f^* - \mu - \sigma \times u) \times \phi(u) du   \\
& = (f^* - \mu) \int_{-\infty}^{\frac{f^* - \mu}{\sigma}} \phi(u) du - \sigma \int_{-\infty}^{\frac{f^* - \mu}{\sigma}} u \phi(u) du   \\
& = (f^* - \mu) \times \Phi(\frac{f^* - \mu}{\sigma}) + \frac{\sigma}{\sqrt{(2 \pi)}} \times \int_{-\infty}^{\frac{f^* - \mu}{\sigma}} u * exp(-\frac{u^2}{2})  \\
& = (f^* - \mu) \times \Phi(\frac{f^* - \mu}{\sigma}) + \frac{\sigma}{\sqrt{(2 \pi)}} \times [exp(-\frac{u^2}{2})]^{\frac{f^* - \mu}{\sigma}}_{-\infty} \\
& = (f^* - \mu) \times \Phi(\frac{f^* - \mu}{\sigma}) + \sigma \phi(\frac{f^* - \mu}{\sigma}) - \sigma \phi(-\infty)  \\
& = (f^* - \mu) \times \Phi(\frac{f^* - \mu}{\sigma}) + \sigma \phi(\frac{f^* - \mu}{\sigma}) - 0 \\
\end{align}
$$
										
Looking at the formula, it is easy to see that we're optimizing the space by trying to exploit points with a low mean and explore points with a high variance. 

It can be imported using:

``` python
from bbo.heuristics.surrogate_models.next_parameter_strategies import expected_improvement
```
As with MPI, the EI is computed over all data points and then optimized with brute force minimization.

### Examples

Like in the [introduction](introduction.md) example, we will optimize the Ackley function, using all three acquisition function and Gaussian Processes as the surrogate function.

``` python
import numpy as np

class Ackley:
    def __init__(self):
        print("I'm the Ackley function ! Good luck finding my optimum !")
        
    def compute(self, array_2d):
        return -20 * np.exp(-0.2 * np.sqrt(0.5 * (array_2d[0]**2 + array_2d[1]**2))) - np.exp(0.5 * (np.cos(2 * np.pi * array_2d[0]) + np.cos(2 * np.pi * array_2d[1]))) + np.exp(1) + 20
    
parametric_grid = np.array([np.arange(-10, 10, 1), np.arange(-5, 5, 1)])
```

We will test three different strategies:
* Using the surrogate as a merit function and using a L-BFGS-B technique to optimize it
* Maximizing the probability of improvement
* Maximizing the expected improvement

In each case, we are going to build an object of class <code>BBOptimizer</code> and then call the <code>optimize</code> and <code>summarize</code> method on it. When using surrogate models as the heuristic of choice, the following arguments should be specified:
* <code>heuristic</code>: its value must be obviously set to "surrogate_model"
* <code>regression_model</code>: the function that should be used for regressing the curve at each iteration
* <code>next_parameter_strategy</code>: the function that should be used for acquisition

``` python
from bbo.optimizer import BBOptimizer

from sklearn.gaussian_process import GaussianProcessRegressor

from bbo.optimizer import BBOptimizer
from bbo.heuristics.surrogate_models.next_parameter_strategies import L_BFGS_B_minimizer, expected_improvement, maximum_probability_improvement 
```

#### Next parameter strategy: using the surrogate as the merit function

``` python
fake_black_box = Ackley()
bb_obj = BBOptimizer(black_box = fake_black_box, # the black-box to optimize
                     parameter_space = parametric_grid, # the grid on which to perform the optimization
                     initial_sample_size=3, # the initial size of the sample
                     heuristic="surrogate_model", # the name of the heuristics to use
                     max_iteration=5, # the maximum number of iterations
                     # the following arguments are specific to surrogate modeling:
                     regression_model=GaussianProcessRegressor, # the regression function
                     next_parameter_strategy=L_BFGS_B_minimizer) # the acquisition function
```

#### Next parameter strategy: maximizing the MPI

``` python
fake_black_box = Ackley()
bb_obj = BBOptimizer(black_box = fake_black_box, 
                     parameter_space = parametric_grid, # the grid on which to perform the optimization
                     initial_sample_size=3, # the initial size of the sample
                     heuristic="surrogate_model", # the name of the heuristics to use
                     max_iteration=10, # the maximum number of iterations
                     # the following arguments are specific to surrogate modeling:
                     regression_model=GaussianProcessRegressor, # the regression function
                     next_parameter_strategy=maximum_probability_improvement) # the acquisition function
```

#### Next parameter strategy: maximizing the EI

``` python
fake_black_box = Ackley()
bb_obj = BBOptimizer(black_box = fake_black_box, 
                     parameter_space = parametric_grid, # the grid on which to perform the optimization
                     initial_sample_size=3, # the initial size of the sample
                     heuristic="surrogate_model", # the name of the heuristics to use
                     max_iteration=10, # the maximum number of iterations
                     # the following arguments are specific to surrogate modeling:
                     regression_model=GaussianProcessRegressor, # the regression function
                     next_parameter_strategy=expected_improvement) # the acquisition function
```

#### Using a custom acquisition function

It is possible to build a custom acquisition function by creating a function that accept the two arguments <code>function</code> and <code>ranges</code>. We're gonna build a function that randomly selects a data point in the grid at each iteration (not recommended at all in production :wink:).

``` python
from numpy.random import uniform

def my_crazy_acquisition_function(func, ranges, **kwargs):
    """
    An acquisition function that is totally out of control by selecting a random data point!
    """
    random_draw = [np.random.choice(axis, 1, replace=False).tolist()
                   for axis in ranges.T]
    return random_draw
```

``` python
fake_black_box = Ackley()
bb_obj = BBOptimizer(black_box = fake_black_box, 
                     parameter_space = parametric_grid, # the grid on which to perform the optimization
                     initial_sample_size=3, # the initial size of the sample
                     heuristic="surrogate_model", # the name of the heuristics to use
                     max_iteration=10, # the maximum number of iterations
                     # the following arguments are specific to surrogate modeling:
                     regression_model=GaussianProcessRegressor, # the regression function
                     next_parameter_strategy=my_crazy_acquisition_function) # the acquisition function
```

Similarly as in the [introduction](introduction.md), we must call the `optimize` method on the `bb_obj` object in order to get the optimization results. The `summarize` method returns a summary of the optimization.

## Simulated annealing
The simulated annealing heuristic is a hill-climbing algorithm
which can probabilistically accept a worse solution than the current one. The probability of
accepting a value worse than the current one decreases with the number of iterations: this
introduces the notion of the system's "temperature" (hence the analogy of with metal annealing).

The temperature is a value that decreases overtime according to a cooling schedule which defines
how the temperature decrease per iteration. As the temperature lowers, the probability of moving
upward (*i.e.* accepting a worse solution) decreases until it reaches 0 and the system cannot
move anymore.

### General principles

The original algorithm goes as follow:

``` python
next_parameter = neighbor(current_parameter)
current_fitness = f(current_parameter)
next_fitness = f(next_parameter)

if next_fitness < current_fitness:
    return N(next_parameter)

else:
    L = random(0, 1)
    P = probability_acceptance(next_fitness, current_fitness, current_temperature)
    if P > L:
        return neighbor(next_parameter)
    else:
        return current_parameter
T = cooling_schedule(T)
```


In some variant, the algorithm can spend several steps in the same temperature.

From this definition, we see that three functions need to be defined in order to implement the algorithm:

* ** The neighboring function <code>neighbor</code>**: given a data point in the sample space, this function returns a point that can be considered as a neighboring data point.

* **The acceptance probability function <code>probability_acceptance</code>**: this function decides the probability of accepting a value lower than the current state. It has to have the following property $lim_{T \rightarrow 0} \mathbb{P}(P(y_{new}, y_{old}, T)) = 1$, so that the probability of accepting worse solution goes down as the temperature reduces.

* **The cooling schedule of cooling function <code>cooling_schedule</code>**: this function computes at iteration $k$.

### Neighboring functions
Any metric can be used to compute the neighbor of a parameter on the grid. There is only one option for now: the <code>hop_to_next_value</code> function which performs a rabdom walk on the parameter grid. The neighboring functions are available in the module `bbo.heuristics.simulated_annealing.neighbor_functions`.

### Acceptance probability function

The commonly used acceptance probability function is the Metropolis acceptance criterion:

$$\mathcal{P} = exp(\frac{y_{old} - y_{new}}{T_k})$$ $T_k$ being the temperature at round $k$.

`bbo` does not provide any acceptance probability other than the Metropolis criterion.


### Cooling schedules
A cooling schedule is a decreasing function. Various different implementation of cooling schedules exist in the literature, with no clear concensus on the best one. Each cooling schedule depend on a cooldown factor, here noted $\alpha$, and an initial temperature $T_0$.

In `bbo`, the following schedules have been implemented:

* *Exponential multiplicative cooling (Kirkpatrick, Gelatt and Vecchi (1983))*: this is the suggestion of the initial paper that described the simulated annealing algorithm: $T_k = \alpha^k T_0$ $0 < \alpha < 1$

* *Logarithmical multiplicative cooling (Aarts, E.H.L. & Korst, J., 1989)*:
$T_k = \frac{T_0}{1 + \alpha log(k+1)}$
$\alpha > 1$

* *Linear multiplicative cooling*:
$T_k = \frac{T_0}{1 + \alpha k }$ $\alpha > 0$

These built-in functions are available in the module `bbo.heuristics.simulated_annealing.cooldown_functions`.

In the spirit of `bbo`, you can build your own cooling schedule and use it with the heuristic.

### Algorithm restarts

As the temperature decreases, the simulated annealing algorithm can get stuck in a local optimum and not have enough energy to get out of it. One way to address this issue is to provide the algorithm with a restart mechanism, which sets the temperature back to its initial value. In `bbo`, a restart function is a function which yields a boolean. When this boolean is set to True, the system restarts by going back to the initial value.

Several restart criteria exist in the literature. BBO implements random restarts, which swaps the temperature with the initial value according to a Bernoulli law drawn at each iteration, and a threshold restart, which restarts the system when the energy has gone under a given value. The number of possible restarts is subjected to a budget that can't be exceeded. The different parametrization of the restart (like the number of restarts, the acceptance factors, ..., is given as argument of the BBOptimizer class). The existing restarts can be found at `bbo.heuristics.simulated_annealing.restart_functions`.

### Examples

Like in the previous examples, we will optimize the Ackley function.

``` python
import numpy as np

class Ackley:
    def __init__(self):
        print("I'm the Ackley function ! Good luck finding my optimum !")
        
    def compute(self, array_2d):
        return -20 * np.exp(-0.2 * np.sqrt(0.5 * (array_2d[0]**2 + array_2d[1]**2))) - np.exp(0.5 * (np.cos(2 * np.pi * array_2d[0]) + np.cos(2 * np.pi * array_2d[1]))) + np.exp(1) + 20

parametric_grid = np.array([np.arange(-10, 10, 1), np.arange(-5, 5, 1)]).T
```

In order to perform the optimization, we need to import:
* A neighboring function
* A cooling schedule
* A restart method

``` python
from bbo.optimizer import BBOptimizer
from bbo.heuristics.simulated_annealing.neighbor_functions import hop_to_next_value
from bbo.heuristics.simulated_annealing.cooldown_functions import multiplicative_schedule
from bbo.heuristics.simulated_annealing.restart_functions import random_restart
```

Once each of the `BBOptimizer` objects have been instanciated as wanted, the `optimize` method can be called upon it.

#### No restarts simulated annealing

``` python
# Create fake black-box
fake_black_box = Ackley()

bb_obj = BBOptimizer(black_box = fake_black_box, # the black-box to optimize                     
            parameter_space = parametric_grid, # the grid on which to perform the optimization
            heuristic="simulated_annealing", # the name of the heuristics to use
            initial_sample_size=3, # the initial size of the sample
            max_iteration=10, # the maximum number of iterations
            initial_temperature=100, # the initial temperature
            cooldown_function=multiplicative_schedule, # the cooling schedule
            cooldown_factor=50, # alpha, the cooling factor
            neighbor_function=hop_to_next_value # the neighboring function
            )
```

#### Random restarts simulated annealing

When using restarts, you need to specify a value for the argument <code>max_restart</code>, the function you want to use for restart (in this case, <code>random_restart</code>), and the argument specific to this restart method (in this case, <code>bernouilli_parameter</code>).

``` python
from bbo.heuristics.simulated_annealing.restart_functions import random_restart
```

``` python
bb_obj = BBOptimizer(black_box = fake_black_box, # the black-box to optimize                     
            parameter_space = parametric_grid, # the grid on which to perform the optimization
            heuristic="simulated_annealing", # the name of the heuristics to use
            initial_sample_size=3, # the initial size of the sample
            max_iteration=10, # the maximum number of iterations
            initial_temperature=100, # the initial temperature
            cooldown_function=multiplicative_schedule, # the cooling schedule
            cooldown_factor=50, # alpha, the cooling factor
            neighbor_function=hop_to_next_value, # the neighboring function
            # Restart specific arguments
            restart=random_restart, # the restart function
            bernouilli_parameter=0.3, # the parametrization of the Bernouilli law that triggers the restart
            max_restart=3) # the maximum number of restarts
```

#### Custom restarts and schedules
Simulated annealing can also work with custom restart function and custom cooling schedules. We'll develop them and use them in the <code>BBOptimizer</code>. 

A cooling schedule must return a scalar (which will represent the temperature) and the restart system a boolean (which indicates whether or not the system should restart) and a scalar which represents the temperature to switch to. Because of the wide variety of the functions that can be used, a <code>**kwargs</code> should be passed as expected improvement for each function.

``` python
def my_crazy_cooling_schedule(initial_temperature, current_iteration, cooling_factor=10, **kwargs):
    """
    This is a cooling schedule which decreases by minus the cooling_factor at each iteration.
    """
    return initial_temperature - current_iteration * cooling_factor
```

``` python
def my_crazy_restarts(initial_temperature, current_iteration, **kwargs):
    """
    This function restarts the system at each even number of iterations.
    """
    return current_iteration % 2 == 0, initial_temperature
```

``` python
bb_obj = BBOptimizer(black_box = fake_black_box, # the black-box to optimize                     
            parameter_space = parametric_grid, # the grid on which to perform the optimization
            heuristic="simulated_annealing", # the name of the heuristics to use
            initial_sample_size=3, # the initial size of the sample
            max_iteration=10, # the maximum number of iterations
            initial_temperature=100, # the initial temperature
            cooldown_function=my_crazy_cooling_schedule, # the cooling schedule
            cooldown_factor=50, # alpha, the cooling factor
            neighbor_function=hop_to_next_value, # the neighboring function
            # Restart specific arguments
            restart=my_crazy_restarts, # the restart function
            max_restart=3) # the maximum number of restarts
```

## Genetic algorithms

Genetic algorithms are a type of evolutionary algorithm that mimic natural selection. At each step, the fittest parents for the new offspring are selected and bred in order to yield a new parameter combination. In the process, this new parametrization can randomly undergo a mutation. 

### General principles
The algorithm consists in selecting two combinations of parameters among the set of already tested parametrization, according to a **selection** process that takes into account the fitness of each parent. These two parameters are then combined to create a new one, using a **crossover** method. This newly created combination can undergo a **mutation**, which subtly alters it in order to provide a new combination. The **exploitation** component is embodied by the selection process, while the **exploration** happens when the offspring is mutated.

```python
parent_1, parent_2 =  selection(F, S)
offspring = crossover(parent_1, parent_2)

if random:
     mutation(offspring)

return offspring
```

From this algorithm, we can deduce we need three types of functions:
* Selection functions, that select the two fittest parents
* Crossover functions, that generate a new offspring from two parents
* Mutation function, that alters an offspring into a new one


### Parent selections

While various techniques exist for selecting the parents, <code>BBO</code> implements two possible methods:

* **Probabilistic pick/Roulette Wheel selection**: it consists in picking out the fittest parametrization according to a random law proportional to their fitness value. 

* **Tournament pick**: it consists in randomly drawing two pools of parametrization of a given size and selecting the fittest element of each pool.

*Elitism*, so that the data point with the highest fitness is always selected, can be enforced using a boolean.

Of course, similar to all the heuristics, you can implement your own selection method. The selection functions can be found at <code>bbo.heuristics.genetic_algorithm.selections</code>.

### Crossovers
Crossover is the method by which the two parametrization will merge in order to create a new one. The most common method, as inspired by biology, is to use **single-point crossover**, which consists into randomly splitting each parametrization in two and concatenating the two parents. Variants of this technique are called *n-*points crossover and consist in cutting the parents into $n$ parts and alternatively concatenating them. `bbo` integrates simple and double point crossover.

The crossovers functions can be found at <code>heuristics.genetic_algorithm.crossover</code>.

### Mutations
Mutation is a random event that can happen to the offspring and modify some its values. This ensures some randomness in the breeding process and enforces the **exploration** property of the genetic algorithm. The probability of the event happening is called the **mutation rate**. There are an infinite number of ways to mutate a parametrization into another one. Identically to simulated annealing, `bbo` comes with a mutation as a random walk: an offspring can randomly (according to a Bernouilli of parameter <code>mutation_rate</code>) turn itself into one of its neighbor's on the parameter grid. The mutation functions can be found at <code>bbo.heuristics.genetic_algorithm.mutations</code>.

### Examples

Like in the previous examples, we will optimize the Ackley function.

``` python
import numpy as np

class Ackley:
    def __init__(self):
        print("I'm the Ackley function ! Good luck finding my optimum !")
        
    def compute(self, array_2d):
        return -20 * np.exp(-0.2 * np.sqrt(0.5 * (array_2d[0]**2 + array_2d[1]**2))) - np.exp(0.5 * (np.cos(2 * np.pi * array_2d[0]) + np.cos(2 * np.pi * array_2d[1]))) + np.exp(1) + 20

parametric_grid = np.array([np.arange(-10, 10, 1), np.arange(-5, 5, 1)]).T
```

The different hyperparameters of the genetic algorithms should be loaded as such:

``` python
from bbo.optimizer import BBOptimizer
from bbo.heuristics.genetic_algorithm.mutations import mutate_chromosome_to_neighbor
from bbo.heuristics.genetic_algorithm.selections import tournament_pick, probabilistic_pick 
from bbo.heuristics.genetic_algorithm.crossover import single_point_crossover
```

#### Tournament pick

``` python
fake_black_box = Ackley()
bb_obj = BBOptimizer(black_box = fake_black_box, # the black-box to optimize
                     parameter_space = parametric_grid, # the grid on which to perform the optimization
                     initial_sample_size=3, # the initial size of the sample
                     heuristic="genetic_algorithm", # the name of the heuristics to use
                     max_iteration=10, # the maximum number of iterations
                     time_out=200, # in seconds, the maximum elapsed time
                     # the following arguments are specific to genetic algorithms:
                     mutation_method= mutate_chromosome_to_neighbor, # the mutation function
                     mutation_rate=0.3, # the mutation rate
                     crossover_method=single_point_crossover, # the crossover function
                     selection_method=tournament_pick # the selection function
                     ) 
```

#### Probabilistic pick

``` python
fake_black_box = Ackley()
bb_obj = BBOptimizer(black_box = fake_black_box, # the black-box to optimize
                     parameter_space = parametric_grid, # the grid on which to perform the optimization
                     initial_sample_size=3, # the initial size of the sample
                     heuristic="genetic_algorithm", # the name of the heuristics to use
                     max_iteration=10, # the maximum number of iterations
                     time_out=200, # in seconds, the maximum elapsed time
                     # the following arguments are specific to genetic algorithms:
                     mutation_method= mutate_chromosome_to_neighbor, # the mutation function
                     mutation_rate=0.3, # the mutation rate
                     crossover_method=single_point_crossover, # the crossover function
                     selection_method=probabilistic_pick # the selection function
                     ) 
```

#### Single point crossover

``` python
fake_black_box = Ackley()
bb_obj = BBOptimizer(black_box = fake_black_box, # the black-box to optimize
                     parameter_space = parametric_grid, # the grid on which to perform the optimization
                     initial_sample_size=3, # the initial size of the sample
                     heuristic="genetic_algorithm", # the name of the heuristics to use
                     max_iteration=10, # the maximum number of iterations
                     time_out=200, # in seconds, the maximum elapsed time
                     # the following arguments are specific to genetic algorithms:
                     mutation_method= mutate_chromosome_to_neighbor, # the mutation function
                     mutation_rate=0.3, # the mutation rate
                     crossover_method=single_point_crossover, # the crossover function
                     selection_method=probabilistic_pick # the selection function
                     ) 
```

#### Double point crossover

``` python
fake_black_box = Ackley()
bb_obj = BBOptimizer(black_box = fake_black_box, # the black-box to optimize
                     parameter_space = parametric_grid, # the grid on which to perform the optimization
                     initial_sample_size=3, # the initial size of the sample
                     heuristic="genetic_algorithm", # the name of the heuristics to use
                     max_iteration=10, # the maximum number of iterations
                     time_out=200, # in seconds, the maximum elapsed time
                     # the following arguments are specific to genetic algorithms:
                     mutation_method= mutate_chromosome_to_neighbor, # the mutation function
                     mutation_rate=0.3, # the mutation rate
                     crossover_method=double_point_crossover, # the crossover function
                     selection_method=probabilistic_pick # the selection function
                     ) 
```

#### Custom pick function

We'll create our custom picking method. It needs to accept as argument a dictionary with the key "fitness", which contains the values for the fitness, and "parameters", which contains the corresponding data point. It has to return a tuple with two elements, each element corresponding to a parent. We'll create a function which always picks the third and fourth parameter of the list.

``` python
def crazy_custom_pick(history):
    """
    Randomly picks a parameter from the list of available ones.
    """
    return history["parameters"][3,:], history["parameters"][4,:]
```

``` python
fake_black_box = Ackley()
bb_obj = BBOptimizer(black_box = fake_black_box, # the black-box to optimize
                     parameter_space = parametric_grid, # the grid on which to perform the optimization
                     initial_sample_size=5, # the initial size of the sample
                     heuristic="genetic_algorithm", # the name of the heuristics to use
                     max_iteration=10, # the maximum number of iterations
                     time_out=200, # in seconds, the maximum elapsed time
                     # the following arguments are specific to genetic algorithms:
                     mutation_method= mutate_chromosome_to_neighbor, # the mutation function
                     mutation_rate=0.3, # the mutation rate
                     crossover_method=single_point_crossover, # the crossover function
                     selection_method=crazy_custom_pick # the selection function
                     ) 
```