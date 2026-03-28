# VU Performance Oriented Computing -- Sheet 04
Author: Marco Fröhlich

## Task A -- Memory profiling

The total heap allocation peaked with $24.5$ MiB for a short amount of time and than dropping back to around $22$ MiB which then gratually reduces to $20$ MiB at the end of execution.

![total heap allocation](total_heap_allocation.png)

The allocation at peak consists mostly of blocks with an individual size of $4$ MiB. Most of these blocks instantly decrease and then build up in size over the rest of the execution time.

![detail heap allocation](heap_allocation.png)

The runtimes of the script with and without the massif tool enabled where as follows:

| type   | average runtime | variance  |
| ------ | --------------- | --------- |
| normal | 32.188 sec      | 0.157 sec |
| massif | 63.372 sec      | 0.597 sec |

As can be seen from the data, when the massif tool is enabled the runtime nearly doubles and the variance also increases significantly.


## Task B -- Measuring CPU counters
