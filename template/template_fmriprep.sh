#!/bin/sh

# This bash script is to run fmriprep
# The script is generated based on the toolbox abcd_fmri_preprocess (/template/template_fmriprep.sh)
# created on {$date_time$}

# Use command to submit this job:
# $ {$job_submit_command$}

echo -e "Start fmriprep at `date +%F-%H:%M:%S`\n"

# ======== settings ======== #

# subject
subject={$subject$}
session={$session$}
folder_label="sub-"$subject"_ses-"$session

# singularity file for fmriprep
file_fmriprep={$file_fmriprep$}
# number of thread to run fmriprep
n_thread={$n_thread$}
# maximum memory (MB) to run fmriprep
max_mem={$max_mem$}

# directory of BIDS folder
dir_bids={$dir_bids$}
# directory of BIDS_QC folder
dir_bids_qc={$dir_bids_qc$}
# directory of fmriprep output folder
dir_fmriprep={$dir_fmriprep$}
# directory to store temporary files
dir_fmriprep_work={$dir_fmriprep_work$}

# directory of this fmriprep output: sub-*_ses-*
dir_fmriprep_sub=$dir_fmriprep/$folder_label
dir_fmriprep_work_sub=$dir_fmriprep_work/$folder_label

# optional settings for the preprocessing
n_dummy={$n_dummy$}
output_space={$output_space$}

file_bids_qc=$dir_bids_qc/$folder_label.txt

# license file for FreeSurfer
file_fs_license={$file_fs_license$}

# log file
file_log={$file_log$}

# clean up previous results
if test -d "$dir_fmriprep_sub"; then
    rm -rf $dir_fmriprep_sub/*
fi
if test -d "$dir_fmriprep_work_sub"; then
    rm -rf $dir_fmriprep_work_sub/*
fi

# prepare bids filter file if file_bids_qc exists
file_bids_filter=$dir_bids_qc/$folder_label.text
python_bids_filter={$python_bids_filter$}
if test -f "$file_bids_qc"; then
    echo -e "\nDetect BIDS_QC file ($folder_label.text)\n"

    source activate {$dir_conda_env$}

    python "$python_bids_filter" \
      --sub $subject \
      --ses $session \
      --bids $dir_bids \
      --bids-qc $dir_bids_qc \
      --fmriprep-work $dir_fmriprep_work

    # change dir_bids
    dir_bids="$dir_fmriprep_work_sub/BIDS"
fi

# ======================== #

# run fmriprep

unset PYTHONPATH

singularity run --cleanenv $file_fmriprep \
   $dir_bids $dir_fmriprep_sub participant \
   --nthreads $n_thread --mem_mb $max_mem \
   --fs-license-file $file_fs_license \
   --dummy-scans $n_dummy \
   --cifti-output "91k" \
   -w $dir_fmriprep_work_sub \
   --participant-label $subject \
   --output-space $output_space \
   >> "$file_log" 2>&1


echo -e "Finish fmriprep at `date +%F-%H:%M:%S`\n"
