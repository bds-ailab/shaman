# Optimization engine

The optimization engine is a stand-alone Python library that can be used either through the REST API or a command-line interface. It is installed on a node, separate from the compute nodes, so that it does not interfere with the running application. 
    
The engine is separated into two distinct modules:
* A generic black-box library which comes out of the box with the framework
* A wrapper which transforms the tunable component into a conceptual black-box
    
## The black-box optimizer
        
The black-box optimizer module performs the black-box optimization process, by relying on the stand-alone optimization library [bbo](../bbo/introduction.md).`bbo` allows to optimize any Python object with a `compute` method that takes as input a vector corresponding to a parametrization and outputs a scalar corresponding to the target value.
    
## The black-box wrapper

The black-box wrapper module transforms the component undergoing tuning so that it can be considered as a black-box by the optimizer module. It must be adapted to each specific use-case.
        
Its practical implementation consists in developing a Python object that enables the manipulation of the component by building a `.compute` method that takes as input the parameters of the component and outputs the corresponding target value, as specified when registering the component. This value is then sent to the optimizer for processing.
An important point to remember is that runs are required to be independent from each other for the optimizer to work properly, so that there is no interaction between parametrization. For example, to optimize I/O accelerators', we clear the system's cache at each iteration of the optimizer to make sure there is no dependence from one run to another.