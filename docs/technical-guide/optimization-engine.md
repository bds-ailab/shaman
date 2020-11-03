   \subsection{Optimization engine}
    The optimization engine is a stand-alone Python library that can be used either through the REST API or a command-line interface. It is installed on a node, separate from the compute nodes, so that it does not interfere with the running application. 
    
    The engine, schematically described in figure~\ref{fig:wrapper}, is separated into two distinct modules:
    \begin{itemize}
        \item A generic black-box library which comes out of the box with the framework
        \item A wrapper which transforms the tunable component into a conceptual black-box
    \end{itemize}
    
        
        \begin{figure*}[t]
        \centering
        \includesvg[scale=0.5]{figures/wrapper.svg}
        \caption{\label{fig:wrapper}Schematic representation of the optimization engine}
        \end{figure*}

        \subsubsection{The black-box optimizer}
        
        The black-box optimizer module performs the black-box optimization process. Its main functionality is to optimize on a specified grid any Python object which satisfies the requirement of having a \verb|.compute| method that takes as input a vector corresponding to a parametrization and outputs a scalar corresponding to the target value. It integrates the three heuristics described in section~\ref{sec:ThBack}. A Python API provides abstractions to add new heuristics with minimal development cost. Adding a new optimization technique is thus straightforward.
        
        \subsubsection{The black-box wrapper}

        The black-box wrapper module transforms the component undergoing tuning so that it can be considered as a black-box by the optimizer module. It must be adapted to each specific use-case.\\
        
        Its practical implementation consists in developing a Python object that enables the manipulation of the component by building a \verb|.compute| method that takes as input the parameters of the component and outputs the corresponding target value. To use the framework for a custom component, the user must develop their own wrapper.
        
        In our practical implementation for I/O accelerators, the corresponding \verb|.compute| method is a method which takes as input the parameters of the accelerator to tune. The parameters of the accelerators are then set as environment variables and passed through the workload manager in order to parametrize the accelerator. The application execution time is recorded by adding a \verb|time| command and parsing its value in the output file of the workload manager. This value is then sent to the optimizer for processing.
        An important point to remember is that runs are required to be independent from each other for the optimizer to work properly, so that there is no interaction between parametrization. For example, in our case, we clear the system's cache at each iteration of the optimizer to make sure there is no dependence from one run to another.