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


# Exercise B

My implementation uses `mmap()` to allocate a huge amount of memory at once, during the first `malloc()` call of a program/thread. After that as defined in a bump allocator only a pointer is moved. The memory gets unmapped once the thread or program exist, a call of `free()` resets the memory pointer to the beginning of the arena, like in `malloc()` arbitrary data is contained in the memory locations. In my implementation the arena has a size of 512MB per thread, otherwise the tester program ran out of memory. Even though the measurements with standard `malloc` claim that more memory is needed during the runtime, but the overhead memory seams not be used on the heap.

As expected my implementation does not spend any measurable time with system calls, since it handles memory by itself in user space, expect the initial calls for the arena space. But the rest of the data is too good to be true, therefor I am not convinced that this simple implementation would hold up in a real world application.

| implementation | sytem time [sec] | real time [sec] | max memory [Mb] |
| -------------- | ---------------- | --------------- | --------------- |
| default        | 114.491          | 170-704         | 517.502         |
| custom         | 0.0              | 5.123           | 9.624           |

According to these measurements the speed-up of my implementation in real time is $\sim 33.32$ times, and also it is $\sim 53.77$ times more memory efficient.
