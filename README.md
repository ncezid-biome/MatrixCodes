# MatrixCodes
Script to assign hierarchical nomenclature to samples present in a distance matrix, using user-defined thresholds in a single-linkage framework


## Installation
git clone https://github.com/ncezid-biome/MatrixCodes.git

Note: script uses default python v3 library installed on system (#!/usr/bin/python3)


## usage
cd MatrixCodes/

./MatrixCodes.py -mt bl -t "100, 50, 25, 12, 6" matrix.tsv


## Example (using ExampleData/BL_matrix_100.tsv)
./MatrixCodes.py -mt bl -t "88, 60, 28, 10, 1" ExampleData/BL_matrix_100.tsv
