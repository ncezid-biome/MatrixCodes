#!/usr/bin/python3

import sys

with open(sys.argv[1], 'r') as matrixFile:
	matrix = [row.split('\t') for row in matrixFile]
	minVal = int(min([min(map(int, row[1:])) for row in matrix]))
	maxVal = int(max([max(map(int, row[1:])) for row in matrix]))
	histogram = [0 for v in range(maxVal+1)]
	for r, row in enumerate(matrix):
		for c, col in enumerate(row[1:]):
			if r==c:
				continue
			histogram[int(col)] += 1
	for h, histVal in enumerate(histogram):
		print("{}\t{}".format(h, '.'*int(histVal*100/max(histogram))))