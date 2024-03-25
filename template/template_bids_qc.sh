#!/bin/sh

# This bash script is to run qc on BIDS formatted MRI data
# The script is generated based on the toolbox abcd_fmri_preprocess (/template/template_qc_raw.sh)
# created on {$date_time$}

# Use command to submit this job:
# $ {$job_submit_command$}

echo -e "Start qc_bids at `date +%F-%H:%M:%S`\n"

# ======== settings ======== #

# subject
subject={$subject$}
session={$session$}
folder_label="sub-"$subject"_ses-"$session

# python file to do qc on bids in toolbox
file_qc_bids={$file_qc_bids$}

# directory of bids
dir_bids={$dir_bids$}

# directories of qc output folder and temporary folder
dir_bids_qc={$dir_bids_qc$}

# ======================== #

# activate conda environment

source activate {$dir_conda_env$}

python "$file_qc_bids" --bids "$dir_bids" --sub "$subject" --ses "$session" -o "$dir_bids_qc"

echo -e "Finish qc_bids at `date +%F-%H:%M:%S`\n"

