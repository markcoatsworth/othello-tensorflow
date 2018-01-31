#!/bin/bash

# Run x number of tests
dt=$(date '+%Y-%m-%d-%H-%M-%S');
output_filename="test-result-$dt.out"
echo "output_filename=$output_filename"
for i in `seq 1 7`; do
	pypy othello.py --robot-battle >> $output_filename
done

