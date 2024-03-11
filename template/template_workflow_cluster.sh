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

# directory for scripts, temporary folder of each step
dir_script_sub={$dir_script_sub$}
dir_bids_temp_sub={$dir_bids_temp_sub$}
dir_fmriprep_temp_sub={$dir_fmriprep_temp_sub$}
dir_xcpd_temp_sub={$dir_xcpd_temp_sub$}

# choice of step to run
# ['raw2bids', 'fmriprep', 'xcpd', 'report']
run_raw2bids={$run_raw2bids$}
run_fmriprep={$run_fmriprep$}
run_xcpd={$run_xcpd$}
run_collect={$run_collect$}

# run raw2bids.sh
if [ "${run_raw2bids}" -eq "1" ]; then
    echo -e "\nStart raw2bids.sh : `date +%F-%H:%M:%S`\n"
    jobID=$({$job_submit_command_raw2bids$})

    status=$(qstat | grep "$jobID" | awk '{print $5}')
    while [ -n "$status" ];
    do
        sleep 60
        status=$(qstat | grep "$jobID" | awk '{print $5}')
    done
    echo -e "\nFinish raw2bids.sh : `date +%F-%H:%M:%S`\n"

    echo 'remove temp file in raw2bids which uses'
    du -sh ${dir_bids_temp_sub}
    rm -rf ${dir_bids_temp_sub}
fi

# run fmriprep.sh
if [ "${run_fmriprep}" -eq "1" ]; then
    echo -e "\nStart fmriprep.sh : `date +%F-%H:%M:%S`\n"
    jobID=$({$job_submit_command_fmriprep$})

    status=$(qstat | grep "$jobID" | awk '{print $5}')
    while [ -n "$status" ];
    do
        sleep 60
        status=$(qstat | grep "$jobID" | awk '{print $5}')
    done
    echo -e "\nFinish fmriprep.sh : `date +%F-%H:%M:%S`\n"

    echo 'remove temp file in fmriprep which uses'
    du -sh ${dir_fmriprep_temp_sub}
    rm -rf ${dir_fmriprep_temp_sub}
fi

# run xcpd.sh
if [ "${run_xcpd}" -eq "1" ]; then
    echo -e "Start xcpd.sh : `date +%F-%H:%M:%S`\n"
    jobID=$({$job_submit_command_xcpd$})

    status=$(qstat | grep "$jobID" | awk '{print $5}')
    while [ -n "$status" ];
    do
        sleep 60
        status=$(qstat | grep "$jobID" | awk '{print $5}')
    done
    echo -e "Finish xcpd.sh : `date +%F-%H:%M:%S`\n"

    echo 'remove temp file in xcpd which uses'
    du -sh ${dir_fmriprep_xcpd_sub}
    rm -rf ${dir_fmriprep_xcpd_sub}
fi

# run collect
if [ "${run_collect}" -eq "1" ]; then
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

