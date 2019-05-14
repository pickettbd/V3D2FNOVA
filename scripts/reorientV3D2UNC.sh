#! /bin/bash

# make sure gnu programs work on macOS
AWK="awk"
BASENAME="basename"
DIRNAME="dirname"
READLINK="readlink"
if [ "`uname`" == "Darwin" ]
then
	AWK="g${AWK}"
	BASENAME="g${BASENAME}"
	DIRNAME="g${DIRNAME}"
	READLINK="g${READLINK}"
fi

# set scripts directory
SCRIPTS_DIR=$(${READLINK} -f `${DIRNAME} "${BASH_SOURCE[0]}"`)

# run the command
for fn in "$@"
do
	dn=`${DIRNAME} "${fn}"`
	sfx=".${fn##*.}"
	bn=`${BASENAME} "${fn}" "${sfx}"`

	time "${AWK}" -f "${SCRIPTS_DIR}/reorient.awk" -- \
		'X=>-Y' \
		'Y=>X' \
		"${fn}" \
		> "${dn}/${bn}_reoriented${sfx}"
done

exit $?

