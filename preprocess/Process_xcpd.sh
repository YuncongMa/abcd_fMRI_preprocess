#!/bin/sh

####################################################################################
# Yuncong Ma, 3/4/2024
# This script is to process ABCD fMRI data
# use bash to run this job
# bash /cbica/home/mayun/Projects/ABCD/Script/preprocess/Process_xcpd.sh
####################################################################################

# main folder
dir_main=/cbica/home/mayun/Projects/ABCD
# log file
file_log=$dir_main/Log/Process_xcpd.log
if test -f "$file_log"
then
    rm ${file_log}
fi
# log files for submitted jobs
dir_log_job=$dir_main/Log/Process_xcpd
mkdir -p $dir_log_job


echo -e "\nRunning : Process_xcpd" >> $file_log
echo -e "Start time : `date +%F-%H:%M:%S`\n" >> $file_log

# fmriprep results
dir_fmriprep=/cbica/home/mayun/Projects/ABCD/fmriprep
dir_sub=$(find $dir_fmriprep -mindepth 1 -maxdepth 1 -type d -name 'sub-*')
dir_sub=($dir_sub)

let N_sub=${#dir_sub[@]}
echo -e "Found $N_sub subfolders:\n" >> $file_log
let N_sub=$N_sub-1
for i in $(seq 0 $N_sub)
do
    sub[i]=$(basename ${dir_sub[i]})
    echo -e "  "${sub[i]} >> $file_log
done

# computation resource
n_thread=4
max_mem=10
job_mem='11G'
# Directory for temporary files
dir_xcpd_work=/cbica/home/mayun/Projects/ABCD/xcpd_work
mkdir -p $dir_xcpd_work

# control to avoid submitting too many jobs at the same time
Wait=1

# xcpd
file_xcpd=/cbica/home/mayun/Projects/ABCD/Tool/xcp_d-0.6.2.simg

# freesurfer license file
file_fs=/cbica/home/mayun/Projects/Toolbox/freesurfer/license.txt

# output dir
dir_output=/cbica/home/mayun/Projects/ABCD/xcpd

# let N_sub=0
echo -e "\nSubmit jobs: \n" >> $file_log
for i in $(seq 0 $N_sub)
do
    # input and output
    dir_fmriprep_sub=${dir_sub[i]}
    dir_output_sub=$dir_output/${sub[i]}
    mkdir -p $dir_output_sub
    echo -e "  Input "$dir_fmriprep_sub >> $file_log
    echo -e "  Output "$dir_output_sub >> $file_log
    
    # log
    file_log_job=$dir_log_job/xcpd_${sub[i]}.log
    if test -f "$file_log_job"
    then
        rm ${file_log_job}
    fi

    # preprocessimg parameters
    n_dummy=10
    FWHM=4.8
    confound='36P'
    bp_low=0.01
    bp_high=0.1
    bp_order=4
    fd_threshold=0.2

    sub_id=$(echo ${sub[i]} | sed 's/....//')
    
    # Submit job
    jib=$(qsub -terse -j y -pe threaded $n_thread -l h_vmem=$job_mem -o $file_log_job \
        $dir_main/Script/preprocess/Submit_xcpd.sh \
        --file-xcpd $file_xcpd \
        --nthreads $n_thread --memory $max_mem \
        -log $file_log_job \
        --fs-license-file $file_fs \
        --n_dummy $n_dummy \
        -fmriprep $dir_fmriprep \
        -output $dir_output \
        -FWHM $FWHM \
        -confound $confound \
        -bp_low $bp_low \
        -bp_high $bp_high \
        -bp_order $bp_order \
        -fd_threshold $fd_threshold \
        --work_dir $dir_xcpd_work \
        --participant-label $sub_id)
    
    echo -e "job ID = "$jib"\n" >> $file_log
    
    # control to avoid parallel downloading
    sleep $Wait
done
echo -e "\nAll jobs are submitted\n" >> $file_log




