#! /bin/bash

# run the command
python3 "${SCRIPTS_DIR}/reformat.py" \
	--samples-file "data/sample.list" \
	--demo-file "data/demographics.csv" \
	--condition "data/conditions.list" \
	--input-dir "data/input" \
	--output-prefix "data/output/" \
	--output-suffix ".csv" \
	--num-trials 5 \
	--last

exit $?

