#!/bin/sh

####################################################################################
# Yuncong Ma, 3/4/2024
# This script is to submit jobs to use XCP-D on ABCD data
# use qsub to run this job
####################################################################################

# For use as a function
parse()
{
    # Default setting
    n_thread=
    memory=
    subject=
    file_xcpd=
    file_fs_license=
    n_dummy=
    FWHM=
    confound=36P
    bp_low=
    bp_high=
    bp_order=4
    fd_threshold=
    dir_fmriprep=
    dir_output=
    dir_work=
    file_log=
    
    while [ -n "$1" ];
    do
        case $1 in
            --nthreads)
                n_thread=$2;
            shift 2;;
            --memory)
                memory=$2;
            shift 2;;
            --file-xcpd)
                file_xcpd=$2;
            shift 2;;
            --subject)
                subject=$2;
            shift 2;;
            --fs-license-file)
                file_fs_license=$2;
            shift 2;;
            --n_dummy)
                n_dummy=$2;
            shift 2;;
            -fmriprep)
                dir_fmriprep=$2;
            shift 2;;
            -output)
                dir_output=$2;
            shift 2;;
            --participant-label)
                subject=$2;
            shift 2;;
            -FWHM)
                FWHM=$2;
            shift 2;;
            -confound)
                confound=$2;
            shift 2;;
            -bp_low)
                bp_low=$2;
            shift 2;;
            -bp_high)
                bp_high=$2;
            shift 2;;
            -bp_order)
                bp_order=$2;
            shift 2;;
            -fd_threshold)
                fd_threshold=$2;
            shift 2;;
            --work_dir)
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

echo -e "\Start to running XCP-D" >> $file_log
echo -e "Start time : `date +%F-%H:%M:%S`\n" >> $file_log

# Print out input parameters
echo -e "file_xcpd = "$file_xcpd >> $file_log
echo -e "n_thread = "$n_thread >> $file_log
echo -e "memory = "$memory >> $file_log
echo -e "subject = "$subject >> $file_log
echo -e "n_dummy = "$n_dummy >> $file_log
echo -e "FWHM = "$FWHM >> $file_log
echo -e "confound = "$confound >> $file_log
echo -e "bp_low = "$bp_low >> $file_log
echo -e "bp_high = "$bp_high >> $file_log
echo -e "bp_order = "$bp_order >> $file_log
echo -e "fd_threshold = "$fd_threshold >> $file_log

echo -e "file_fs_license = "$file_fs_license >> $file_log

echo -e "dir_work = "$dir_work >> $file_log

echo -e "dir_fmriprep = "$dir_fmriprep >> $file_log
echo -e "dir_output = "$dir_output >> $file_log
echo -e "file_log = "$file_log >> $file_log



# Run singularity
unset PYTHONPATH

singularity run --cleanenv $file_xcpd \
 --participant_label $subject \
 --omp-nthreads $n_thread \
 --mem_gb $memory \
 --input-type fmriprep \
 --dummy-scans $n_dummy \
 --smoothing $FWHM \
 -p $confound \
 --lower-bpf $bp_low \
 --upper-bpf $bp_high \
 --bpf-order $bp_order \
 -f $fd_threshold \
 --skip-parcellation \
 --fs-license-file $file_fs_license \
 --work_dir $dir_work \
 $dir_fmriprep $dir_output participant

echo -e "\nFinished at `date +%F-%H:%M:%S`" >> $file_log
