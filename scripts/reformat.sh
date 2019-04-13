#! /bin/bash

# ensure we're running from the correct location
SCRIPTS_DIR=$(greadlink -f `dirname "${BASH_SOURCE[0]}"`)
MAIN_DIR=$(greadlink -f `dirname "${SCRIPTS_DIR}/"`)
RUN_DIR=$(greadlink -f .)

if [ "${RUN_DIR}" != "${MAIN_DIR}" ] || [ "${MAIN_DIR}/scripts" != "${SCRIPTS_DIR}" ]
then
	printf "\n\t%s\n\t%s\n\n" "Script must be run from ${MAIN_DIR}" "You are currently at:   ${RUN_DIR}" 1>&2
	exit 1
fi

# set some handy variables
DATA_DIR="${MAIN_DIR}/data"
INPUT_SAMPLES_LIST="${DATA_DIR}/samples.list"
INPUT_CONDITIONS_LIST="${DATA_DIR}/conditions.list"
INPUT_DEMOGRAPHICS_FILE="${DATA_DIR}/demographics.csv"
INPUT_BASE_DIR="${DATA_DIR}/input"
OUTPUT_DIR="${DATA_DIR}/output"
OUTPUT_FILE_PREFIX="${OUTPUT_DIR}/" # keep the slash if this is a directory
OUTPUT_FILE_SUFFIX=".csv"
NUM_TRIALS=10

# handle directory structure
mkdir -p "${OUTPUT_DIR}" &> /dev/null

# run the command
EXIT_CODE=0

while read COND
do
	python3 "${SCRIPTS_DIR}/reformat.py" \
		"${INPUT_SAMPLES_LIST}" \
		"${INPUT_DEMOGRAPHICS_FILE}" \
		"${COND}" \
		"${INPUT_BASE_DIR}" \
		"${OUTPUT_FILE_PREFIX}" \
		"${OUTPUT_FILE_SUFFIX}" \
		${NUM_TRIALS}

	LOCAL_EXIT_CODE=$?

	# exit
	if [ ${LOCAL_EXIT_CODE} -eq 0 ]
	then
		printf "%s: %s\n" "${COND}" "SUCCESS" 1>&2
	else
		printf "%s: %s\n" "${COND}" "FAILED" 1>&2
		EXIT_CODE=${LOCAL_EXIT_CODE}
	fi
	
done < "${INPUT_CONDITIONS_LIST}"

exit ${EXIT_CODE}
