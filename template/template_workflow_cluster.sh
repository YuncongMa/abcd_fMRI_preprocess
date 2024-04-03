#!/bin/sh

# This bash script is to run the abcd_fmri_preprocess workflow for a dataset
# The script is generated based on the toolbox abcd_fmri_preprocess (/template/template_workflow_cluster.sh)
# created on {$date_time$}

# Use command to run this job:
# $ {$job_submit_command$}


echo -e "\nRunning : workflow_cluster.sh"

# directory for scripts, temporary folder of each step
dir_script_cluster={$dir_script_cluster$}
# main directory to store results
dir_main={$dir_main$}
# file for resubmit use, set to an existing file if wants to re-run some subjects and sessions
file_resubmit_info={$file_resubmit_info$}
# flag to continue submitting workflow jobs not started yet
flag_continue={$flag_continue$}

# configuration for job submission control
maxProgress={$maxProgress$}
minSpace={$minSpace$}

# folder to store failed workflows
dir_failed=$dir_main/Failed
mkdir -p $dir_failed

# folder to store final results passing completion check
dir_result=$dir_main/Result
mkdir -p $dir_result

# get subject session information based on sub folder names in Script_Cluster
if [[ -z $file_resubmit_info ]]; then
    list_subject_session=($(find "$dir_script_cluster" -type d))
    list_subject_session=("${list_subject_session[@]:1}")
else
    if test -f "$file_resubmit_info"; then
        list_subject_session=($(cat "$file_resubmit_info"))
        N_sub_ses=${#list_subject_session[@]}
        for ((i = 0; i < $N_sub_ses; i++)); do
            list_subject_session[$i]=$dir_script_cluster/${list_subject_session[$i]}
        done
    else
        echo -e "[Error]: Cannot find the file defined in file_resubmit_info\n"
        exit
    fi
fi

# number of jobs to submit
let N_sub_ses=${#list_subject_session[@]}
echo -e "There are $N_sub_ses subjects"

# number of progresses in running
progress_running=0
# number of finished progresses
n_progress_done=0

# use index starting from 0
flag_progress=( $(for i in $(seq 0 $N_sub_ses); do echo 0; done) )
progress_jobID=

while [ "$n_progress_done" -lt "$N_sub_ses" ]; do
    for ((i = 0; i < $N_sub_ses; i++)); do

        # check the space available
        let spaceAvail=$(df -k $dir_main | tail -1 | awk '{print $4}')/1024/1024
        if [ "$spaceAvail" -lt "$minSpace" ]; then
            echo -e "\n Warning: available space is only $spaceAvail GB.\nIt is smaller than $minSpace GB.\n Stop submitting new jobs.\n"
            echo "$progress_running jobs are in running, and $n_progress_done jobs are finished"
            break
        fi

        # check whether there is result if flag_continue==1
        if [ "$flag_continue" -eq "1" ] && [ "${flag_progress[$i]}" -eq "0" ]; then
            if test -d $dir_result/${list_subject_session[$i]}; then
                flag_progress[$i]=2
                ((n_progress_done++))
                echo "job is already done for ${list_subject_session[$i]}"
            fi
        fi

        # submit a workflow job
        if [ "${flag_progress[$i]}" -eq "0" ]; then
            # check the number of running progress
            if [ "$progress_running" -eq "$maxProgress" ]; then
                continue
            fi
            bashFile=${list_subject_session[$i]}"/workflow.sh"
            logFile=${list_subject_session[$i]}"/Log_workflow.log"
            # clean previous log file
            if test -f "$logFile"; then
                rm -rf $logFile
            fi

            jobID=$(qsub -terse -j y -pe threaded 1 -l h_vmem=5G -o $logFile $bashFile)
            echo "submit job for ${list_subject_session[$i]} with jobID=${jobID}"
            flag_progress[$i]=1
            progress_jobID[$i]="$jobID"
            ((progress_running++))
            echo "$progress_running jobs are in running, and $n_progress_done jobs are finished"
            sleep 0.5
        fi

        # check completion of the job
        if [ "${flag_progress[$i]}" -eq "1" ]; then
            jobID=${progress_jobID[$i]}
            status=$(qstat | grep "$jobID" | awk '{print $5}')
            if [ -z "$status" ]; then
                echo "job is finished for ${list_subject_session[i]}"
                ((progress_running--))
                ((n_progress_done++))
                echo "$progress_running jobs are in running, and $n_progress_done jobs are finished"
                flag_progress[$i]=2
            fi
        fi
    done
    sleep 60
done

echo -e "\nFinished workflow_cluster.sh"
