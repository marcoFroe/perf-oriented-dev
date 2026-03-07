# VU Performance Oriented Computing -- Sheet 01
Author: Marco Fröhlich

## Exercise 1 - Preparation

### Parameters
Following is a description of the parameters needed for each program. I considered the programs as black boxes and did not change any source code files.

- *delannoy*: problem size between 1 and 22
- *filegen*: needs instruction on how many directories and files to generate and at what size -- `./filegen <num_directories> <num_files_per_directory> <min_file_size> <max_file_size>`
- *filesearch*: no arguments required
- *mmul*: no arguments required
- *nbody*: no arguments required
- *qap*: path to the problem data

### Results
Each of the runs was executed 10 times and the average and variance is shown in the table as `<avg>[<variance>]`. If not stated otherwise the parameter selection was done by experimenting with the settings and choosing some interesting examples and also not exceeding the computation time limit on the LCC3.

| Program  | parameters | Comment | real time [s] | CPU time [s] | system time [s] | max memory usage [KB] |
|----------|------------|---------|---------------|--------------|-----------------|-----------------------|
| delannoy |            |         |               |              |                 |                       |
| filegen  |            |         |               |              |                 |                       |
| mmul     |            |         |               |              |                 |                       |
| nbody    |            |         |               |              |                 |                       |
| qap      |            |         |               |              |                 |                       |

## Exercise 2 - Experiments