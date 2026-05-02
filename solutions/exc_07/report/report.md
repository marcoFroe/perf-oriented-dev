# VU Performance Oriented Computing -- Sheet 07

Author: Marco Fröhlich

# Disclaimer

Since I did this sheet during the downtime of LCC3 all results are only based on measurements on my local desktop machine. The setup is as follows:

- CPU: AMD Ryzen 7 7700X - 8 core
- OS: Kubuntu 24.04
- Kernel: 6.17.0-22-generic(64-bit)
- RAM: 2x16GB DDR5-5600Hz
- compiler version:
- ninja version: 1.11.1

# Exercise A -- Preloading General Allocators

I had to edit the source code of the `allscale_api` since otherwise it would not compile on my machine. The change I made was in the `/allscale_api/code/utils/include/allscale/utils/large_array.h` file, I added the following line `#include <cstdint>`, this was suggested by the compiler.

Experiment runs: 10
Conversion factor Kb -> Mb: 1/1000

| implementation | sytem time [sec]    | real time [sec]      | max memory [Mb]          |
| -------------- | ------------------- | -------------------- | ------------------------ |
| baseline       | 9.444 (var: 0.0092) | 24.672 (var: 0.0282) | 1 244.583 (var: 128.532) |
| mimalloc       | 8.505 (var: 0.0063) | 23.947 (var: 0.0364) | 1 321.747 (var: 983.724) |
| rpmalloc       | 9.647 (var: 0.0085) | 23.950 (var: 0.0610) | 1 219.742 (var: 97.099)  |

The `mimalloc` variant needed the least amount of runtime, but on the same time the most amount of memory, with an very high variance too. Overall the memory consumption did not vary very much over all `malloc` implementations. In terms of system time, the other `malloc` implementations did use about $1/2$ second less time, which is not covered in the variance of the experiments.

# Exercise B

My implementation uses `mmap()` to allocate a huge amount of memory at once, during the first `malloc()` call of a program/thread. After that as defined in a bump allocator only a pointer is moved. The memory gets unmapped once the thread or program exist, a call of `free()` resets the memory pointer to the beginning of the arena, like in `malloc()` arbitrary data is contained in the memory locations. In my implementation the arena has a size of 512MB per thread, otherwise the tester program ran out of memory. Even though the measurements with standard `malloc` claim that more memory is needed during the runtime, but the overhead memory seams not be used on the heap.

As expected my implementation does not spend any measurable time with system calls, since it handles memory by itself in user space, expect the initial calls for the arena space. But the rest of the data is too good to be true, therefor I am not convinced that this simple implementation would hold up in a real world application.

Experiment runs: 10

| implementation | sytem time [sec]      | real time [sec]      | max memory [Mb]       |
| -------------- | --------------------- | -------------------- | --------------------- |
| default        | 114.491 (var: 0.928 ) | 170.704 (var: 0.968) | 517.502 (var: 32.490) |
| custom         | 0.0 (var: 0)          | 5.123 (var: 0.0347)  | 9.624 (var: 4.551)    |

According to these measurements the speed-up of my implementation in real time is $\sim 33.32$ times, and also it is $\sim 53.77$ times more memory efficient.
