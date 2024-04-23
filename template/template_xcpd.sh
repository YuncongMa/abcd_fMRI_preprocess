#!/bin/sh

# This bash script is to run fmriprep
# The script is generated based on the toolbox abcd_fmri_preprocess (/template/template_xcpd.sh)
# created on {$date_time$}

# Use command to submit this job:
# $ {$job_submit_command$}


echo -e "Start xcpd at `date +%F-%H:%M:%S`\n"

# ======== settings ======== #

# subject
subject={$subject$}
session={$session$}
folder_label="sub-"$subject"_ses-"$session

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
dir_xcpd_work={$dir_xcpd_work$}

# directory of this fmriprep output: sub-*_ses-*
dir_fmriprep_sub=$dir_fmriprep/$folder_label
# for xcpd
dir_xcpd_sub=$dir_xcpd/$folder_label
dir_xcpd_cifti_sub=$dir_xcpd_cifti/$folder_label
dir_xcpd_work_sub=$dir_xcpd_work/$folder_label

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

# clean up previous results
if test -d "$dir_xcpd_work_sub"; then
    rm -rf $dir_xcpd_work_sub/*
fi
if test -d "$dir_xcpd_cifti_sub"; then
    rm -rf $dir_xcpd_cifti_sub/*
fi
if test -d "$dir_xcpd_sub"; then
    rm -rf $dir_xcpd_sub/*
fi

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
 --work_dir $dir_xcpd_work_sub \
 --cifti \
 $dir_fmriprep_sub $dir_xcpd_cifti_sub participant \
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
 $dir_fmriprep_sub $dir_xcpd_sub participant \
 >> $file_log 2>&1

# clean work
if test -d "$dir_xcpd_work_sub"; then
    rm -rf $dir_xcpd_work_sub/*
fi

echo -e "Finish xcpd at `date +%F-%H:%M:%S`\n"
