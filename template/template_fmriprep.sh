#!/bin/sh

# This bash script is to run fmriprep
# The script is generated based on the toolbox abcd_fmri_preprocess (/template/template_fmriprep.sh)
# created on {$date_time$}

# Use command to submit this job:
# $ {$job_submit_command$}

echo -e "Start time : `date +%F-%H:%M:%S`\n" 

unset PYTHONPATH

# setting

file_fmriprep={$file_fmriprep$}
n_thread={$n_thread$}
max_mem={$max_mem$}

dir_bids={$dir_bids$}
dir_output={$dir_output$}
dir_fmriprep_work={$dir_fmriprep_work$}

subject={$subject$}

n_dummy={$n_dummy$}
output_space={$output_space$}

file_fs_license={$file_fs_license$}

# run fmriprep

singularity run --cleanenv $file_fmriprep \
 $dir_bids $dir_output participant \
 --nthreads $n_thread --mem_mb $max_mem \
 --fs-license-file $file_fs_license \
 --dummy-scans $n_dummy \
 --cifti-output "91k" \
 -w $dir_fmriprep_work \
 --participant-label $subject \
 --output-space $output_space --use-aroma

echo -e "Finished time : `date +%F-%H:%M:%S`\n" 
