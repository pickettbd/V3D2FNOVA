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
	printf "\n\t%s\n\t%s\n\n" "Script must be run from ${MAIN_DIR}" "You are currently at:   ${RUN_DIR}" 1>&2
	exit 1
fi

# set some handy variables
DATA_DIR="${MAIN_DIR}/data"
INPUT_MEASUREMENTS_LIST="${DATA_DIR}/measurements.list"
INPUT_CONDITIONS_LIST="${DATA_DIR}/conditions.list"
CONTROL_COND="control"
INPUT_DIR="${DATA_DIR}/output"
OUTPUT_DIR="${DATA_DIR}/output"
OUTPUT_FILE_PREFIX="${OUTPUT_DIR}/all_" # if this is a directory, leave a trailing slash
OUTPUT_FILE_SUFFIX=".csv"

# handle directory structure
mkdir -p "${OUTPUT_DIR}" &> /dev/null

# run the command
EXIT_CODE=0


while read MEAS
do
	NON_CONTROL_COND_COUNT=0
	declare -a CMD_ARGS
	CMD_ARGS=('-d' ',')

	while read COND
	do
		if [ "${COND}" == "${CONTROL_COND}" ]
		then
			NON_CONTROL_COND_COUNT=$((NON_CONTROL_COND_COUNT+1))
		else
			CMD_ARGS+=(${INPUT_DIR}/${COND}_${MEAS}.csv)
		fi

	done < "${INPUT_CONDITIONS_LIST}"

	for i in `seq 1 1 ${NON_CONTROL_COND_COUNT}`
	do
		CMD_ARGS+=(${INPUT_DIR}/${CONTROL_COND}_${MEAS}.csv)
	done

	paste ${CMD_ARGS[@]} > "${OUTPUT_FILE_PREFIX}${MEAS}${OUTPUT_FILE_SUFFIX}"

	LOCAL_EXIT_CODE=$?

	# exit
	if [ ${LOCAL_EXIT_CODE} -eq 0 ]
	then
		printf "%s: %s\n" "${MEAS}" "SUCCESS" 1>&2
	else
		printf "%s: %s\n" "${MEAS}" "FAILED" 1>&2
		EXIT_CODE=${LOCAL_EXIT_CODE}
	fi

done < "${INPUT_MEASUREMENTS_LIST}"

exit ${EXIT_CODE}

