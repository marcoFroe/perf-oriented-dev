# VU Performance Oriented Computing -- Sheet 03
Author: Marco Fröhlich

## Task A -- Traditional profiling
For this analysis the program versions `_a` and `_b` were used. The files where compiled for the release build, the only modification to the `cmake` file was the addition of the `-pg` flag for the profiler output generation.

### Home laptop
Home Device Information:
- CPU: 8 $\times$ AMD Ryzen 7 3700U (4 physical cores)
- RAM: 29,3 GiB of 
- OS: Kubuntu 24.04 
- gprof version: (GNU Binutils for Ubuntu) 2.42

#### `npb_bt_a`:
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

#### `npb_bt_b`: 
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


### LCC3GNU 
- gprof version: 2.30-128.el8_10
 

#### `npb_bt_a`:
Total runtime: 69.14 seconds


**Flat profile:**

| % time | cumulative seconds | self seconds | calls     | self ms/call | total ms/call | name        |
| ------ | ------------------ | ------------ | --------- | ------------ | ------------- | ----------- |
| 30.77  | 21.27              | 21.27        | 146029716 | 0.00         | 0.00          | binvcrhs    |
| 18.40  | 33.99              | 12.72        | 146029716 | 0.00         | 0.00          | matmul_sub  |
| 12.43  | 42.59              | 8.59         | 201       | 42.74        | 105.69        | y_solve     |
| 11.76  | 50.72              | 8.13         | 201       | 40.45        | 103.40        | z_solve     |
| 10.70  | 58.12              | 7.40         | 201       | 36.82        | 99.77         | x_solve     |
| 9.49   | 64.68              | 6.56         | 202       | 32.48        | 32.48         | compute_rhs |
| 5.51   | 68.49              | 3.81         | 146029716 | 0.00         | 0.00          | matvec_sub  |
| 0.46   | 68.81              | 0.32         | -         | -            | -             | add         |

#### `npb_bt_b`:
Total runtime: 288.58 seconds


**Flat profile:**

| % time | cumulative seconds | self seconds | calls     | self ms/call | total ms/call | name        |
| ------ | ------------------ | ------------ | --------- | ------------ | ------------- | ----------- |
| 30.77  | 88.78              | 88.78        | 609030000 | 0.00         | 0.00          | binvcrhs    |
| 18.86  | 143.21             | 54.43        | 609030000 | 0.00         | 0.00          | matmul_sub  |
| 12.70  | 179.86             | 36.65        | 201       | 182.31       | 443.38        | z_solve     |
| 11.64  | 213.45             | 33.59        | 201       | 167.14       | 428.20        | y_solve     |
| 10.80  | 244.62             | 31.17        | 201       | 155.10       | 416.16        | x_solve     |
| 9.45   | 271.88             | 27.25        | 202       | 134.92       | 134.92        | compute_rhs |
| 4.71   | 285.48             | 13.60        | 609030000 | 0.00         | 0.00          | matvec_sub  |
| 0.54   | 287.04             | 1.56         | -         | -            | -             | add         |

#### Analysis:
