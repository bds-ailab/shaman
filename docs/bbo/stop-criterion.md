# Stop criterion

When running the optimization algorithm, the easiest stop criterion is based either on a budget of possible steps (also called exhaustion based) or on a time-out based on the maximum elapsed time for the algorithm: once the budget has been spent, the algorithm stops and returns the best found parametrization. This is the default behavior of `bbo` and by extension `SHAMan`. However,this criterion can be inefficient, as it has no adaptive quality on the tuned system. That's why SHAMan implements three other types of stop criteria to improve the convergence performance.

# Improvement based criterion

# Movement based criterion

## Number of distinct parametrization

## Distance measured over the parametric grid