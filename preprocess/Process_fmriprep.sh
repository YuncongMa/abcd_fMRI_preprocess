#!/bin/sh

####################################################################################
# Yuncong Ma, 2/29/2024
# This script is to process ABCD fMRI data
# use bash to run this job
# bash /cbica/home/mayun/Projects/ABCD/Script/preprocess/Process_fmriprep.sh
####################################################################################

# main folder
dir_main=/cbica/home/mayun/Projects/ABCD
# log file
file_log=$dir_main/Log/Process_fmriprep.log
if test -f "$file_log"
then
    rm ${file_log}
fi
# log files for submitted jobs
dir_log_job=$dir_main/Log/Process_fmriprep
mkdir -p $dir_log_job


echo -e "\nRunning : Process_fmriprep" >> $file_log
echo -e "Start time : `date +%F-%H:%M:%S`\n" >> $file_log

# BIDS format
dir_bids=/cbica/home/mayun/Projects/ABCD/BIDS
dir_sub=$(find $dir_bids -mindepth 1 -maxdepth 1 -type d)
dir_sub=($dir_sub)

let N_sub=${#dir_sub[@]}-1
echo -e "Found $N_sub subfolders:\n" >> $file_log
for i in $(seq 0 $N_sub)
do
    sub[i]=$(basename ${dir_sub[i]})
    echo -e "  "${sub[i]} >> $file_log
done

# computation resource
n_thread=4
max_mem=47000
# Directory for temporary files
dir_work=/cbica/home/mayun/Projects/ABCD/fmriprep_Work
mkdir -p $dir_work

# control to avoid submitting too many jobs at the same time
Wait=1

# fmriprep
file_fmriprep=/cbica/home/mayun/Toolbox/nipreps_fmriprep_23.0.2.simg

# freesurfer license file
file_fs=/cbica/home/mayun/Projects/Toolbox/freesurfer/license.txt

# output dir
dir_output=/cbica/home/mayun/Projects/ABCD/fmriprep

# let N_sub=0
echo -e "\nSubmit jobs: \n" >> $file_log
for i in $(seq 0 $N_sub)
do
    # input and output
    dir_bids_sub=${dir_sub[i]}
    dir_output_sub=$dir_output/${sub[i]}
    mkdir -p $dir_output_sub
    echo -e "  Input "$dir_bids_sub >> $file_log
    echo -e "  Output "$dir_output_sub >> $file_log
    
    # log
    file_log_job=$dir_log_job/fmriprep_${sub[i]}.log
    if test -f "$file_log_job"
    then
        rm ${file_log_job}
    fi

    # preprocessimg parameters
    n_dummy=10
    sub_id=$(echo ${sub[i]} | sed 's/....//')
    
    # Submit job
    jib=$(qsub -terse -j y -pe threaded $n_thread -l h_vmem=48G -o $file_log_job \
        /cbica/home/mayun/Projects/ABCD/Script/preprocess/Submit_fmriprep.sh \
        --file-fmriprep $file_fmriprep \
        --nthreads $n_thread --mem_mb $max_mem \
        -log $file_log_job \
        --fs-license-file $file_fs \
        --dummy-scans $n_dummy \
        -bids $dir_bids \
        -output $dir_output \
        --participant-label $sub_id \
        -w $dir_work)
    
    echo -e "job ID = "$jib"\n" >> $file_log
    
    # control to avoid parallel downloading
    if [ "$i" -lt "1" ]
    then
        echo -e "start waiting for the 1st job\n" >> $file_log
        sleep $Wait
    fi
done
echo -e "\nAll jobs are submitted\n" >> $file_log




