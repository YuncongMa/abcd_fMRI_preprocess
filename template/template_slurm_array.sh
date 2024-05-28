#!/bin/bash
#SBATCH --job-name={$name_array_job$}
#SBATCH --output=array_job_%A_%a.out
#SBATCH --array=0-{$N$}  # Adjust this based on the number of lines in your commands.txt
#SBATCH --mem=1
SLURM_ARRAY_TASK_MAX={$max_workflow$} 

# Yuncong Ma
# This script is to submit a SLURM array job to control the execution of workflows for all subjects and sessions
# use submit_slurm_array.sh to run this job
# created on {$date_time$}

# command to run each workflow
file_array_job={$file_array_job$}

# Read the command to run from the text file at the line number specified by SLURM_ARRAY_TASK_ID
CMD=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" $file_array_job)

# Execute the command
eval $CMD