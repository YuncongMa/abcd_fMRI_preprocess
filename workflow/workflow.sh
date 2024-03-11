#!/bin/bash
# Yuncong Ma, 3/8/2024
# Control the overall workflow in a cluster environment
# use qsub to run this job

dir_main='/cbica/home/mayun/Projects/ABCD'
# dir_main='/Users/yuncongma/Documents/Document/fMRI/Myworks/ABCD'

dir_script_cluster="$dir_main/Script_Cluster"

list_subject_session=($(find "$dir_script_cluster" -type d))

N_sub_ses=${#list_subject_session[@]}
maxProgress=50

progress_running=0
declare -a flag_progress
declare -a progress_jobID
n_progress_done=0

while [ "$progress_running" -lt "$N_sub_ses" ]; do
    for ((i = 0; i < N_sub_ses; i++)); do
        if [ "${flag_progress[$i]}" -eq 0 ]; then
            echo "submit job for ${list_subject_session[i]}"
            bashFile="${list_subject_session[i]}/workflow.sh"
            logFile="${list_subject_session[i]}/Log_workflow.log"
            jobID=$(qsub -terse -j y -pe threaded 1 -l h_vmem=5G -o "$logFile" "$bashFile")
            flag_progress[$i]=1
            progress_jobID[$i]=$jobID
            ((progress_running++))
            sleep 0.5
        else
            jobID=${progress_jobID[i]}
            status=$(qstat | grep "$jobID" | awk '{print $5}')
            if [ -z "$status" ]; then
                ((progress_running--))
            fi
        fi
        if [ "$progress_running" -eq "$maxProgress" ]; then
            sleep 60
            break
        fi
    done
done
