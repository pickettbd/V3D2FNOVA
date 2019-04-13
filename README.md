# V3D2FNOVA
Prepare Visual 3D (V3D) data for FNOVA at UNC-CH

## Purpose
This project is intended as a data transformation step. Normalized V3D files (tab-separated value) are previously generated for each subject and each condition. These are then transformed using this simple tool. The output is somewhat strangly-formatted, but it is the format needed for an FNOVA analysis. This process is employed by researchers at UNC-CH as part of a vGRF (vertical Ground Reaction Force) manipulation project. It could, however, be used or modified for other purposes.

## Directory Structure
Scripts are written to be run from the main directory (not inside scripts or inside data). The repo preserves the existance of the data directory, but leaves it empty for you to fill. Once an input directory is decided upon, there must be a subdirectory structure of ${SAMPLE}/${CONDITION}/ with file names of ${SAMPLE}_${CONDITION}_normalized.txt.

## Dependencies
Python 3. At least a version with f-strings.

## Usage
If you ever use this tool, open an issue and ask me to actually fill this section out. Otherwise, I assume you can modify the "handy" variables in reformat.sh and/or modify the code in reformat.{sh,py}.

