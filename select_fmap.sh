#! /bin/bash

# Yuncong Ma, 2/20/2024
# This bash file does NOT process Dti or task data
# Corrected directories and settings

# Given a subject ID, session, and tgz directory:
#   4) Select the best SEFM

## Necessary dependencies
# dcm2bids (https://github.com/DCAN-Labs/Dcm2Bids)
# microgl_lx (https://github.com/rordenlab/dcm2niix)
# pigz-2.4 (https://zlib.net/pigz)
# run_order_fix.py (in this repo)
# sefm_eval_and_json_editor.py (in this repo)

SUB=$1 # Full BIDS formatted subject ID (sub-SUBJECTID)
VISIT=$2 # Full BIDS formatted session ID (ses-SESSIONID)
TGZDIR=$3 # Path to directory containing all .tgz for this subject's session

ABCD2BIDS_DIR=$4 # directory of ABCD dicom2bids
ROOT_BIDSINPUT=$5
ScratchSpaceDir=$6
FSL_DIR=$7 # Get FSL directory paths
DIR_PYTHON_YM=$8 # directory of yuncong's Python code for abcd

participant=`echo ${SUB} | sed 's|sub-||'`
session=`echo ${VISIT} | sed 's|ses-||'`

TempSubjectDir=${ScratchSpaceDir}

# select best fieldmap and update sidecar jsons
echo ${TempSubjectDir}/BIDS_unprocessed/${SUB}/${VISIT}/fmap
if [ -d ${TempSubjectDir}/BIDS_unprocessed/${SUB}/${VISIT}/fmap ]; then
    echo `date`" :RUNNING SEFM SELECTION AND EDITING SIDECAR JSONS"
    ${DIR_PYTHON_YM}/sefm_eval_and_json_editor_yuncong.py ${TempSubjectDir}/BIDS_unprocessed ${FSL_DIR} --participant-label=${participant} --output_dir $ROOT_BIDSINPUT
fi
