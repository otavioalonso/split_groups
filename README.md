# Split groups

Takes a list of participants and splits into groups mixing/grouping specified
categories.

## Usage

positional arguments:
  participants          tsv file containing list of participants.

optional arguments:
  -h, --help            show this help message and exit
  -n N\_GROUPS           Number of groups to split.
  -i ITERATIONS         Number of iterations in the optimization process.
  -o OUTPUT             Output file with group number column appended.
  -a                    Use simulated annealing.
  -m MIX\_COLUMNS [MIX\_COLUMNS ...]
                        Mix groups by values found in the specified columns.
                        Useful to separate people belonging to the same
                        specified class. Use <column_index>:<weight> to
                        specify a weight for each column. If you want to group
                        classes instead of mixing them, use a negative weight.
  -c CLUSTER\_COLUMNS [CLUSTER\_COLUMNS ...]
                        Cluster similar values found in the specified columns.
                        Useful to get people with similar age together in the
                        same group. Use <column_index>:<weight> to specify a
                        weight for each column. If you want to disperse
                        instead of clustering values, use a negative weight.

## Example

```bash
./split\_groups.py participants.txt -n 3 -m 0:2 2:-0.3 -c 3 -i 1000 -o groups.txt
```

Divides participants in 3 groups, mixing column 0 categories with weight 2, column 2 categories with weight -0.3 (i.e. groups this category), cluster values in column 3 together. Uses 1000 iterations to optimize and outputs to file groups.txt

