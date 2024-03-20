#!/bin/bash
# Yuncong Ma, 3/19/2024
# Control the overall workflow in a cluster environment
# use qsub to run this job
# dir_main=/cbica/home/mayun/Projects/ABCD
# qsub -terse -j y -pe threaded 1 -l h_vmem=5G -o $dir_main/Log/Log_workflow_cluster.log $dir_main/Script/workflow/workflow_cluster.sh

# For use as a function
parse()
{
    # Default setting
    dir_main='/cbica/home/mayun/Projects/ABCD'
    dir_script_cluster="$dir_main/Script_Cluster"
    # limit the max number of running progress, and check the space available
    maxProgress=20  # 20 max workflows
    minSpace=500  # 500GB free space at least to submit new jobs
    
    while [ -n "$1" ];
    do
        case $1 in
            --main)
                dir_main=$2;
            shift 2;;
            --scriptCluster)
                dir_script_cluster=$2;
            shift 2;;
            --maxProgress)
                maxProgress=$2;
            shift 2;;
            --minSpace)
                minSpace=$2;
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


echo -e "\nRunning : workflow_cluster.sh"


# folder to store failed workflows
dir_failed=$dir_main/Failed
mkdir -p $dir_failed

# folder to store final results passing completion check
dir_result=$dir_main/Result
mkdir -p $dir_result

# get sub
list_subject_session=($(find "$dir_script_cluster" -type d))


let N_sub_ses=${#list_subject_session[@]}-1

progress_running=0
n_progress_done=0

# use index starting from 0
flag_progress=( $(for i in $(seq 0 $N_sub_ses); do echo 0; done) )
progress_jobID=

while [ "$n_progress_done" -lt "$N_sub_ses" ]; do
    for ((i = 1; i <= $N_sub_ses; i++)); do
        # check the space available
        let spaceAvail=$(df -k $dir_main | tail -1 | awk '{print $4}')/1024/1024
        if [ "$spaceAvail" -lt "$minSpace" ]; then
            echo -e "\n Warning: available space is only $spaceAvail GB.\nIt is smaller than $minSpace GB.\n Stop submitting new jobs.\n"
            echo "$progress_running jobs are in running, and $n_progress_done jobs are finished"
            break
        fi
        # submit a workflow job
        if [ "${flag_progress[$i]}" -eq "0" ]; then
            # check the number of running progress
            if [ "$progress_running" -eq "$maxProgress" ]; then
                continue
            fi
            bashFile=${list_subject_session[$i]}"/workflow.sh"
            logFile=${list_subject_session[$i]}"/Log_workflow.log"
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