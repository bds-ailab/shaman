<template>
  <!-- Copyright 2020 BULL SAS All rights reserved -->
  <div>
    <b-card>
      <b-tabs pills card justified>
        <b-tab title="Purpose" active
          ><b-card-text>
            Modern computer systems, both hardware and software, come with many
            tunable parameters and their parameterization can have a huge impact
            on their performance. This is especially true for the case of HPC
            systems, where performance is one of the most important concern.
            Making sure that the parametrization of the system is optimal is
            thus crucial to the proper operation of an HPC system, such as an
            HPC cluster. Many components of an HPC can be parametrized, for
            example Message Passing Interaces (MPI), storage bays, I/O
            (Input/Output) accelerators, storage bays etc. A set of parameters
            can be determined for each application running on the HPC and using
            a component, or for each type of applications, to maximize the
            performance measurement of the application(s). To find an optimal
            parametrization, auto-tuning methods relying on black-box
            optimization have delivered good results in many different computer
            science fields, including HPC. Black-box optimization refers to the
            optimization of a function of unknown properties, most of the time
            costly to evaluate, which entails a limited number of possible
            evaluations. SHAMan is a new optimization framework which provides
            an out-of-the-box a Web application to perform black-box auto-tuning
            of custom computer components, running on a distributed system
            running the Slurm workload manager. As well as three state-of-art
            heuristics, the framework integrates noise reduction strategies, to
            deal with the possible interference of shared resources for large
            scale HPC systems, and pruning strategies, to reduce to the maximum
            the running times of the optimization experiments.</b-card-text
          ></b-tab
        >
        <b-tab title="Advantages">
          <ul>
            <li>
              Accessibility: the optimization engine is accessible through a Web
              Interface
            </li>
            <li>
              Easy to extend: the optimization engine uses a plug-in
              architecture. So, there is no extra development costs other than
              the development of the heuristic itself.
            </li>

            <li>
              Integrated within the HPC ecosystem: the framework relies on the
              Slurm workload manager to run HPC applications. The microservice
              architecture enables it to have no concurrent interactions with
              the cluster and the application itself.
            </li>

            <li>
              Flexible for a wide range of use-cases: new components can be
              registered through a generalist configuration file.
            </li>

            <li>
              Integrates noise reduction strategies: because of their highly
              dynamic nature and the complexity of applications and software
              stacks, HPC systems are subjected to many interference when
              running in production, which results in a different performance
              measure for each run even with the same system's parametrization.
              Noise reduction strategies are included in the framework to
              account for this case.
            </li>

            <li>
              Integrates pruning strategies: runs with unsuited parametrization
              are aborted, to reduce the elapsed time of the application
            </li>
          </ul>
        </b-tab>
        <b-tab title="Installing a new component"> </b-tab>
        <b-tab title="Architecture"></b-tab>
        <b-tab title="Optimization heuristics"></b-tab>
        <b-tab title="Running without UI"> </b-tab>
      </b-tabs>
    </b-card>
  </div>
</template>
