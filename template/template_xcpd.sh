#!/bin/sh

# This bash script is to run fmriprep
# The script is generated based on the toolbox abcd_fmri_preprocess (/template/template_xcpd.sh)
# created on {$date_time$}

# Use command to submit this job:
# $ {$job_submit_command$}


echo -e "Start time : `date +%F-%H:%M:%S`\n" 

# setting

file_xcpd={$file_xcpd$}
n_thread={$n_thread$}
memory={$memory$}

dir_output={$dir_output$}
dir_xcpd_work={$dir_xcpd_work$}
dir_fmriprep={$dir_fmriprep$}

subject={$subject$}

n_dummy={$n_dummy$}
fwhm={$fwhm$}
confound='{$confound$}'
bp_low={$bp_low$}
bp_high={$bp_high$}
bp_order={$bp_order$}
fd_threshold={$fd_threshold$}

file_fs_license={$file_fs_license$}

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
 $dir_fmriprep $dir_output participant

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
 --work_dir $dir_xcpd_work \
 $dir_fmriprep $dir_output participant

echo -e "Finished time : `date +%F-%H:%M:%S`\n" 
