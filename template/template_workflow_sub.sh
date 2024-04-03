#!/bin/sh

# This bash script is to run the abcd_fmri_preprocess workflow for one subject
# The script is generated based on the toolbox abcd_fmri_preprocess (/template/template_workflow.sh)
# created on {$date_time$}

# Use command to run this job:
# $ {$job_submit_command$}

echo -e "Start workflow.sh : `date +%F-%H:%M:%S`\n"

# information for subject and session
subject={$subject$}
session={$session$}
folder_label="sub-"$subject"_ses-"$session

# directory for scripts, temporary folder of each step
dir_script_cluster={$dir_script_cluster$}
dir_bids_work={$dir_bids_work$}
dir_fmriprep_work={$dir_fmriprep_work$}
dir_xcpd_work={$dir_xcpd_work$}

dir_bids_work_sub=$dir_bids_work/$folder_label
dir_fmriprep_work_sub=$dir_fmriprep_work/$folder_label
dir_xcpd_work_sub=$dir_xcpd_work/$folder_label


# choice of step to run
# ['raw2bids', 'bids_qc', 'fmriprep', 'xcpd', 'report']
run_raw2bids={$run_raw2bids$}
run_bids_qc={$run_bids_qc$}
run_fmriprep={$run_fmriprep$}
run_xcpd={$run_xcpd$}
run_collect={$run_collect$}

# run raw2bids.sh
if [ "${run_raw2bids}" -eq "1" ]; then
    # cleanup log file
    file_log=$dir_script_cluster/$folder_label/Log_raw2bids.log
    if test -f "$file_log"; then
        rm -rf $file_log
    fi

    echo -e "\nStart raw2bids.sh : `date +%F-%H:%M:%S`\n"
    jobID=$({$job_submit_command_raw2bids$})

    status=$(qstat | grep "$jobID" | awk '{print $5}')
    while [ -n "$status" ];
    do
        sleep 60
        status=$(qstat | grep "$jobID" | awk '{print $5}')
    done
    echo -e "\nFinish raw2bids.sh : `date +%F-%H:%M:%S`\n"

fi

# run bids_qc.sh
if [ "${run_bids_qc}" -eq "1" ]; then
    # cleanup log file
    file_log=$dir_script_cluster/$folder_label/Log_bids_qc.log
    if test -f "$file_log"; then
        rm -rf $file_log
    fi

    echo -e "\nStart bids_qc.sh : `date +%F-%H:%M:%S`\n"
    jobID=$({$job_submit_command_bids_qc$})

    status=$(qstat | grep "$jobID" | awk '{print $5}')
    while [ -n "$status" ];
    do
        sleep 60
        status=$(qstat | grep "$jobID" | awk '{print $5}')
    done
    echo -e "\nFinish bids_qc.sh : `date +%F-%H:%M:%S`\n"

fi

# run fmriprep.sh
if [ "${run_fmriprep}" -eq "1" ]; then
    # cleanup log file
    file_log=$dir_script_cluster/$folder_label/Log_fmriprep.log
    if test -f "$file_log"; then
        rm -rf $file_log
    fi

    echo -e "\nStart fmriprep.sh : `date +%F-%H:%M:%S`\n"
    jobID=$({$job_submit_command_fmriprep$})

    status=$(qstat | grep "$jobID" | awk '{print $5}')
    while [ -n "$status" ];
    do
        sleep 60
        status=$(qstat | grep "$jobID" | awk '{print $5}')
    done
    echo -e "\nFinish fmriprep.sh : `date +%F-%H:%M:%S`\n"
fi

# run xcpd.sh
if [ "${run_xcpd}" -eq "1" ]; then
    # cleanup log file
    file_log=$dir_script_cluster/$folder_label/Log_xcpd.log
    if test -f "$file_log"; then
        rm -rf $file_log
    fi

    echo -e "Start xcpd.sh : `date +%F-%H:%M:%S`\n"
    jobID=$({$job_submit_command_xcpd$})

    status=$(qstat | grep "$jobID" | awk '{print $5}')
    while [ -n "$status" ];
    do
        sleep 60
        status=$(qstat | grep "$jobID" | awk '{print $5}')
    done
    echo -e "Finish xcpd.sh : `date +%F-%H:%M:%S`\n"
fi

# run collect
if [ "${run_collect}" -eq "1" ]; then
    # cleanup log file
    file_log=$dir_script_cluster/$folder_label/Log_collect.log
    if test -f "$file_log"; then
        rm -rf $file_log
    fi

    echo -e "Start collect.sh : `date +%F-%H:%M:%S`\n"
    jobID=$({$job_submit_command_collect$})

    status=$(qstat | grep "$jobID" | awk '{print $5}')
    while [ -n "$status" ];
    do
        sleep 10
        status=$(qstat | grep "$jobID" | awk '{print $5}')
    done
    echo -e "Finish collect.sh : `date +%F-%H:%M:%S`\n"
fi

# finish
echo -e "Finish workflow.sh : `date +%F-%H:%M:%S`\n"

