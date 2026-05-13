# VU Performance Oriented Computing -- Sheet 09

Author: Marco Fröhlich

## List Implementations

I choose to implement both list types my self using a common interface to make my life easier with the benchmarking tool. These implementations are very rudimentary and there was no big focus on optimization.

## Benchmarking Tool

To ensure that the compiler does not remove write and read calls the value from the previous read call always XOR's on a buffer value, which is used in the following write call. To support the difference in data size, always the whole memory location gets copied, even though only the first byte of data is used in the described operation. Since an XOR operation on 1 byte of data is a negligible operation compared to the `memcpy()` call required to actually read the data this will not have an impact in the performance.

