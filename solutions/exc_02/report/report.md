# VU Performance Oriented Computing -- Sheet 02
Author: Marco Fröhlich


## Exercise 01 -- External CPU load

All experiments were run 25 times and the average and variance was calculated. In the following only the real time is shown.

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
| filesearch | -          | true      | 0.2516    |     
dasdfasdfll