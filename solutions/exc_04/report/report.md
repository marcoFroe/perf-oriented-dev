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

The events in question are the following:
-  L1-dcache-load-misses    
-  L1-dcache-loads          
-  L1-dcache-prefetch-misses
-  L1-dcache-prefetches     
-  L1-dcache-store-misses   
-  L1-dcache-stores         
-  L1-icache-load-misses    
-  L1-icache-loads          
-  LLC-load-misses          
-  LLC-loads                
-  LLC-prefetch-misses      
-  LLC-prefetches           
-  LLC-store-misses         
-  LLC-stores               
-  branch-load-misses       
-  branch-loads             
-  dTLB-load-misses         
-  dTLB-loads               
-  dTLB-store-misses        
-  dTLB-stores              
-  iTLB-load-misses         
-  iTLB-loads               
-  node-load-misses         
-  node-loads               
-  node-prefetch-misses     
-  node-prefetches          
-  node-store-misses        
-  node-stores              

After some research I found out that most CPUs can record between 4 and 8 counters accurately at the same time. Therefor I choose to go with the lower end of this assumption and split the required events into 6 packages of 4 and one with the remaining 3 events. For none of the combinations `perf` complained that it can not record them at the same time.
