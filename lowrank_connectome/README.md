# Data and codes for the paper "Greedy low-rank algorithm for spatial connectome regression"
  
This repository is split into two directories:
- **data/**  measurement data and matrices stored in .mat files for a test "toy" problem, top_view and flatmap connectivity regressions.
- **matlab/**  greedy low-rank solver in Matlab, test running file and auxiliary plotting routines.

The main file to run is *test_allvis_completion.m* in the **matlab/** directory. It will ask the user to enter the test parameters, run the greedy solver *greedy_lr_solve.m* and save the solution. By default, it will run the toy test problem.

**NOTE!** The real top_view and flatmap experiments might take a lot of CPU time and memory for large ranks!

The total cost of the computed solution can be obtained via the *cost_lr.m* function.

To plot the whole test solution you can use the *plot_test.m* script, and the singular vectors of the solution can be plotted via *plot_svectors.m*. Other files in the **matlab/** directory perform auxiliary plotting tasks. Please refer to individual help messages in each file for more information.

