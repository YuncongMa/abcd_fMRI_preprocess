#!/bin/sh

####################################################################################
# Yuncong Ma, 2/29/2024
# This script is to submit jobs to use fmriprep on ABCD data
# use qsub to run this job
# fmriprep comes with ICA-AROMA and CIFTI output
####################################################################################

# For use as a function
parse()
{
    # Default setting
    n_thread=
    file_fmriprep=
    max_mem=
    file_fs=
    n_dummy=
    dir_bids=
    dir_output=
    sub_id=
    dir_work=
    file_log=
    
    while [ -n "$1" ];
    do
        case $1 in
            --nthreads)
                n_thread=$2;
            shift 2;;
            --file-fmriprep)
                file_fmriprep=$2;
            shift 2;;
            --mem_mb)
                max_mem=$2;
            shift 2;;
            --fs-license-file)
                file_fs=$2;
            shift 2;;
            --dummy-scans)
                n_dummy=$2;
            shift 2;;
            -bids)
                dir_bids=$2;
            shift 2;;
            -output)
                dir_output=$2;
            shift 2;;
            --participant-label)
                sub_id=$2;
            shift 2;;
            -w)
                dir_work=$2;
            shift 2;;
            -log)
                file_log=$2;
            shift 2;;
            -*)
                echo "ERROR:no such option $1"
            exit;;
            *)
            break;;
        esac
    done
}

parse $*

# Start bash processing

echo -e "\Start to running fmriprep" >> $file_log
echo -e "Start time : `date +%F-%H:%M:%S`\n" >> $file_log

# Print out input parameters
echo -e "file_fmriprep = "$file_fmriprep >> $file_log
echo -e "n_thread = "$n_thread >> $file_log
echo -e "max_mem = "$max_mem >> $file_log
echo -e "file_fs = "$file_fs >> $file_log
echo -e "n_dummy = "$n_dummy >> $file_log
echo -e "dir_bids = "$dir_bids >> $file_log
echo -e "dir_output = "$dir_output >> $file_log
echo -e "sub_id = "$sub_id >> $file_log
echo -e "dir_work = "$dir_work >> $file_log
echo -e "file_log = "$file_log >> $file_log



# Run singularity
unset PYTHONPATH

singularity run --cleanenv $file_fmriprep \
 $dir_bids $dir_output participant \
 --nthreads $n_thread \
 --omp-nthreads $n_thread \
 --mem_mb $max_mem \
 --fs-license-file $file_fs \
 --dummy-scans $n_dummy \
 --cifti-output "91k" \
 -w $dir_work \
 --participant-label $sub_id \
 --output-space T1w MNI152NLin6Asym:res-2 MNI152NLin2009cAsym \
 --use-aroma

echo -e "\nFinished at `date +%F-%H:%M:%S`" >> $file_log
