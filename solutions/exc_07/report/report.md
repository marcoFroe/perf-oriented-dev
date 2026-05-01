# VU Performance Oriented Computing -- Sheet 07

Author: Marco Fröhlich

# Disclaimer

Since I had problems login into LCC3 during the time I was doing this sheet, all results are only based on measurements on my local desktop machine. The setup is as follows:

- CPU: AMD Ryzen 7 7700X - 8 core
- OS: Kubuntu 24.04
- Kernel: 6.17.0-22-generic(64-bit)
- RAM: 2x16GB DDR5-5600Hz
- compiler version:
- ninja version: 1.11.1

# Exercise A -- Preloading General Allocators

# Exercise B

My implementation uses `mmap()` to allocate a hugh amount of memory at once, during the first `malloc()` call of a program/thread. After that as defined in a bump allocator only a pointer is moved. The memory gets unmapped once the thread or program exitst, a call of `free()` resets the memory pointer to the beginning of the arena, like in `malloc()` arbitrary data is contained in the memory locations. In my implementation the arena has a size of 512MB per thread, otherwise the tester program ran out of memory. Eventhough the measurements with standard malloc claim that more memory is needed during the runtime, but the overhead memory seams not be used on the heap.

As expected my implementation does not spend any measurable time with system calls, since it handles memory by itself in user space, expect the initial calls for the arena space. But the rest of the data is to good to be true, therefor I am not convinced that this simple implemetation would hold up in a real world application.

| implementation | sytem time [sec] | real time [sec] | max memory [Mb] |
| -------------- | ---------------- | --------------- | --------------- |
| default        | 114.491          | 170-704         | 517.502         |
| custom         | 0.0              | 5.123           | 9.624           |

According to these measuremnts the speed up of my implementation in real time is $\sim 33.32$ times and also it its $\sim 53.77$ times more memory efficient.
