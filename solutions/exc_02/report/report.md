# VU Performance Oriented Computing -- Sheet 02
Author: Marco Fröhlich


## Exercise 01 -- External CPU load

All experiments were run 25 times and the average and variance was calculated. In the following only the real time is shown.
Running the problem under load was done like this inside the `slurm` file:

```bash
tools/load_generator/exec_with_workstation_heavy.sh "python automated_tester/experiment_generator.py --config <CONFIG>
```

Since I spent a lot of time tweaking with experiment setting trying to get any meaningful differences between the normal runtime and the one using the load script I opted to not repeat all experiments on my local machine as well.

### Delannoy

| experiment | parameters | with load | real time | variance |
| ---------- | ---------- | --------- | --------- | -------- |
| delannoy   | 12         | false     | 0.6264    | 3.23e-05 |
| delannoy   | 13         | false     | 3.3676    | 1.52e-04 |
| delannoy   | 14         | false     | 12.3072   | 3.03e-03 |
| delannoy   | 12         | true      | 0.628     | 1.6e-05  |
| delannoy   | 13         | true      | 3.3708    | 2.8e-04  |
| delannoy   | 14         | true      | 12.2724   | 3.2e-03  |

For the `delannoy` experiments introducing external CPU load is not noticeable.

### File Generation

| experiment | parameters | with load | real time | variance |
| ---------- | ---------- | --------- | --------- | -------- |
| filegen    | 10,10      | false     | 0.8252    | 7.85e-02 |
| filgen     | 10,50      | false     | 3.9592    | 6.33e-02 |
| filegen    | 50,50      | false     | 21.2008   | 1.354    |
| filegen    | 10,10      | true      | 0.8144    | 2.90e-02 |
| filgen     | 10,50      | true      | 4.116     | 0.4514   |
| filegen    | 50,50      | true      | 21.7808   | 8.606    |

For the `filegen` experiments introducing external CPU load is slightly noticeable, especially when more files are generated. Especially the variance of runtime gets greater with the load enabled.

### File Search
These experiments where run after using `filegen 1000 150 5120 10240`.

| experiment | parameters | with load | real time | variance  |
| ---------- | ---------- | --------- | --------- | --------- |
| filesearch | -          | false     | 0.2588    | 5.527e-04 |
| filesearch | -          | true      | 0.2516    | 1.473e-04 |

Interestingly for this example the experiment that ran with load enabled was slightly faster and has less variance in the result. The origin of this result is unknown since the experiments were carried out on different nodes and at different times.

### Matrix Multiplication

| experiment | parameters | with load | real time | variance  |
| ---------- | ---------- | --------- | --------- | --------- |
| mmul       | 2000       | false     | 26.814    | 0.4763    |
| mmul       | 2000       | true      | 26.7348   | 0.1233    |
| mmul       | 1000       | false     | 2.0288    | 3.961e-03 |
| mmul       | 1000       | true      | 2.0288    | 3.002e-03 |

Here also the version with load took slightly less time for the bigger problem size. For the smaller size the execution time averaged exactly to the same time, only the variance was slightly higher with load enabled.

### N Body Simulation

| experiment | parameters | with load | real time | variance  |
| ---------- | ---------- | --------- | --------- | --------- |
| nbody      | 1000       | false     | 2.5568    | 6.43e-05  |
| nbody      | 1000       | true      | 2.5884    | 4.73e-05  |
| nbody      | 2000       | false     | 4.2592    | 1.577e-04 |
| nbody      | 2000       | true      | 4.2596    | 1.206e-04 |
| nbody      | 5000       | false     | 9.354     | 4.67e-04  |
| nbody      | 5000       | true      | 9.36      | 6.75e-04  |

Also, here the differences when running with load and without was barely noticeable.


### QAP
| experiment | parameters  | with load | real time | variance   |
| ---------- | ----------- | --------- | --------- | ---------- |
| qap        | chr15a.dat  | false     | 3.4936    | 3.740e-04  |
| qap        | chr15b.dat  | false     | 0.9412    | 1.10e-05   |
| qap        | chr15c.dat  | false     | 3.1834    | 1.273e-04  |
| qap        | chr15a.dat  | true      | 3.5436    | 2.573e-04  |
| qap        | chr15b.dat  | true      | 0.956     | 5.0e-05    |
| qap        | chr15ac.dat | true      | 3.2276    | 1.1107e-04 |

Here the version run with load enabled took slightly longer.

### Conclusion
Apparently the load used does not affect the runtime of the used programs. Or I have not used it correctly.