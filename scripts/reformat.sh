#! /bin/bash

# make sure it works on macOS
DIRNAME="dirname"
READLINK="readlink"
if [ "`uname`" == "Darwin" ]
then
	DIRNAME="g${DIRNAME}"
	READLINK="g${READLINK}"
fi

# set scripts directory
SCRIPTS_DIR=$(${READLINK} -f `${DIRNAME} "${BASH_SOURCE[0]}"`)

# run the command
python3 "${SCRIPTS_DIR}/reformat.py" \
	--demo-file "data/demographics.csv" \
	--conditions-file "data/conditions.list" \
	--per-condition-samples-files \
	--input-dir "data/input" \
	--output-prefix "data/output/" \
	--output-suffix ".csv" \
	--num-trials 5 \
	--last \
	--not-treadmill

exit $?

