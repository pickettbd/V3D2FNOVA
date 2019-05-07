#! /bin/bash

# make sure it works on macOS
READLINK="readlink"
if [ "`uname`" == "Darwin" ]
then
	READLINK="g${READLINK}"
fi

# ensure we're running from the correct location
SCRIPTS_DIR=$(${READLINK} -f `dirname "${BASH_SOURCE[0]}"`)
MAIN_DIR=$(${READLINK} -f `dirname "${SCRIPTS_DIR}/"`)
RUN_DIR=$(${READLINK} -f .)

if [ "${RUN_DIR}" != "${MAIN_DIR}" ] || [ "${MAIN_DIR}/scripts" != "${SCRIPTS_DIR}" ]
then
	printf "\n\t%s\n\t%s\n\n" "Script intended to be run from ${MAIN_DIR}" "You are currently at:          ${RUN_DIR}" 1>&2
fi

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

