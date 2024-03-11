#!/bin/sh

# This bash script is to run fmriprep
# The script is generated based on the toolbox abcd_fmri_preprocess (/template/template_xcpd.sh)
# created on {$date_time$}

# Use command to submit this job:
# $ {$job_submit_command$}


echo -e "Start xcpd at `date +%F-%H:%M:%S`\n"

# ======== settings ======== #

# singularity file for xcp_d
file_xcpd={$file_xcpd$}
# number of thread
n_thread={$n_thread$}
# maximum memory (GB)
memory={$memory$}

# directory of the fmriprep input folder
dir_fmriprep={$dir_fmriprep$}
# directory of the xcpd output folder
dir_xcpd={$dir_xcpd$}
dir_xcpd_cifti={$dir_xcpd_cifti$}
# directory to store temporary files
dir_xcpd_work_sub={$dir_xcpd_work_sub$}

# subject
subject={$subject$}

# optional settings for the preprocessing
n_dummy={$n_dummy$}
fwhm={$fwhm$}
confound='{$confound$}'
bp_low={$bp_low$}
bp_high={$bp_high$}
bp_order={$bp_order$}
fd_threshold={$fd_threshold$}

# license file for FreeSurfer
file_fs_license={$file_fs_license$}

# log file
file_log={$file_log$}

# ======================== #

# run xcp-d

# run cifti version
singularity run --cleanenv $file_xcpd \
 --participant_label $subject \
 --omp-nthreads $n_thread --mem_gb $memory \
 --input-type fmriprep \
 --dummy-scans $n_dummy \
 --smoothing $fwhm \
 -p $confound \
 --lower-bpf $bp_low \
 --upper-bpf $bp_high \
 --bpf-order $bp_order \
 -f $fd_threshold \
 --skip-parcellation \
 --fs-license-file $file_fs_license \
 --work_dir $dir_xcpd_work \
 --cifti \
 $dir_fmriprep $dir_xcpd_cifti participant \
 >> $file_log 2>&1

# run volume version
 singularity run --cleanenv $file_xcpd \
 --participant_label $subject \
 --omp-nthreads $n_thread --mem_gb $memory \
 --input-type fmriprep \
 --dummy-scans $n_dummy \
 --smoothing $fwhm \
 -p $confound \
 --lower-bpf $bp_low \
 --upper-bpf $bp_high \
 --bpf-order $bp_order \
 -f $fd_threshold \
 --skip-parcellation \
 --fs-license-file $file_fs_license \
 --work_dir $dir_xcpd_work_sub \
 $dir_fmriprep $dir_xcpd participant \
 >> $file_log 2>&1

echo -e "Finish xcpd at `date +%F-%H:%M:%S`\n"
