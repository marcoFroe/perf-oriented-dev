# VU Performance Oriented Computing -- Sheet 03
Author: Marco Fröhlich

## Task A -- Traditional profiling
For this analysis the program versions `_a` and `_b` were used. The files where compiled for the release build, the only modification to the `cmake` file was the addition of the `-pg` flag for the profiler output generation.

### Home laptop
Home Device Information:
- CPU: 8 $\times$ AMD Ryzen 7 3700U (4 physical cores)
- RAM: 29,3 GiB of RAM

#### `_a`:
Total Runtime: 47.18 sec

**Flat profile:**

 | % time | cumulative seconds | self seconds | calls     | self ms/call | total ms/call | name        |
 | ------ | ------------------ | ------------ | --------- | ------------ | ------------- | ----------- |
 | 30.82  | 14.54              | 14.54        | 146029716 | 0.00         | 0.00          | binvcrhs    |
 | 15.41  | 21.81              | 7.27         | 146029716 | 0.00         | 0.00          | matmul_sub  |
 | 13.65  | 28.25              | 6.44         | 201       | 32.04        | 72.70         | y_solve     |
 | 12.21  | 34.01              | 5.76         | 202       | 28.51        | 28.51         | compute_rhs |
 | 10.64  | 39.03              | 5.02         | 201       | 24.98        | 65.64         | z_solve     |
 | 9.83   | 43.67              | 4.64         | 201       | 23.08        | 63.75         | x_solve     |
 | 5.21   | 46.13              | 2.46         | 146029716 | 0.00         | 0.00          | matvec_sub  |
 | 1.21   | 46.70              | 0.57         | 201       | 2.84         | 2.84          | add         |

Everything below took less than 1 sec.

#### `_b`: 
Total Runtime: 200.06 seconds

**Flat profile:**

| % time | cumulative seconds | self seconds | calls     | self ms/call | total ms/call | name        |
| ------ | ------------------ | ------------ | --------- | ------------ | ------------- | ----------- |
| 30.72  | 61.45              | 61.45        | 609030000 | 0.00         | 0.00          | binvcrhs    |
| 14.71  | 90.88              | 29.43        | 609030000 | 0.00         | 0.00          | matmul_sub  |
| 13.55  | 117.99             | 27.11        | 201       | 134.88       | 303.55        | y_solve     |
| 12.06  | 142.11             | 24.12        | 202       | 119.41       | 119.41        | compute_rhs |
| 11.22  | 164.56             | 22.45        | 201       | 111.69       | 280.36        | z_solve     |
| 10.81  | 186.18             | 21.62        | 201       | 107.56       | 276.24        | x_solve     |
| 5.17   | 196.52             | 10.34        | 609030000 | 0.00         | 0.00          | matvec_sub  |
| 1.13   | 198.79             | 2.27         | 201       | 11.29        | 11.29         | add         |


