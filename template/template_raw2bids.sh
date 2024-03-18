#!/bin/sh

# This bash script is to run raw2bids.sh
# The script is generated based on the toolbox abcd_fmri_preprocess (/template/template_raw2bids.sh)
# created on {$date_time$}

# Use command to submit this job:
# $ {$job_submit_command$}

echo -e "Start raw2bids at `date +%F-%H:%M:%S`\n"

# ======== settings ======== #

# subject
subject={$subject$}
session={$session$}
folder_label="sub-"$subject"_ses-"$session

# bash file to do raw2bids in toolbox /abcd_raw2bids/abcd_raw2bids.sh
file_raw2bids={$file_raw2bids$}

# dcm2bids
file_dcm2bids={$file_dcm2bids$}

# information of scan list
list_sub_scan={$list_sub_scan$}

# directories of bids output folder and temporary folder
dir_bids={$dir_bids$}
dir_bids_work={$dir_bids_work$}
dir_bids_work_sub=$dir_bids_work/$folder_label

# directory to the toolbox sub-folder ./abcd_raw2bids
dir_abcd_raw2bids={$dir_abcd_raw2bids$}

# log file
file_log={$file_log$}

# ======================== #

# activate conda environment

source activate {$dir_conda_env$}

# run raw2bids

bash $file_raw2bids \
 --subject $subject \
 --session $session \
 --bids $dir_bids \
 --tempDir $dir_bids_work_sub \
 --abcd_raw2bids $dir_abcd_raw2bids \
 --dcm2bids $file_dcm2bids \
 --scanList $list_sub_scan \
 >> $file_log 2>&1

echo -e "Finish raw2bids at `date +%F-%H:%M:%S`\n"
