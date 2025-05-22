# MatrixCodes
Script to assign hierarchical nomenclature to samples present in a distance matrix, using user-defined thresholds in a single-linkage framework


## Installation
git clone https://github.com/ncezid-biome/MatrixCodes.git
cd MatrixCodes/
chmod 777 *

Note: script uses default python v3 library installed on system (#!/usr/bin/python3)


## usage
positional arguments:
  matrixFile            Bottom-left (bl) or Top-right (tr) distance matrix
                        with first column being sample identifiers

required arguments:
  -mt, --matrixType     'bl' or 'tr', corresponding to bottom-left or top-
                        right type of matrix, respectively
  -t, --thresholds      Quoted, comma-separated thresholds in descending order

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Whether to print excessively or not

execution:
./MatrixCodes.py -mt bl -t "100, 50, 25, 12, 6" matrix.tsv


## Example (using ExampleData/BL_matrix_100.tsv)
./MatrixCodes.py -mt bl -t "88, 60, 28, 10, 1" ExampleData/BL_matrix_100.tsv

2025-05-22 11:09:47     Importing matrix values...

2025-05-22 11:09:47: START

................... 99% (Adding key100, avg add time: 0.0s)

2025-05-22 11:09:48: END


key1:   5.3.17

key2:   5.3.17.18.1

key3:   5.3.17

key4:   5.3.17.74

key5:   5.3.17.9.1

key6:   5.3.17

key7:   5.3.17.1.1

key8:   5.3.17.14.1

key9:   5.3.17

key10:  5.3.17

...
