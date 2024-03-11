# Yuncong Ma, 3/8/2024
# Control the overall workflow in a cluster environment
# use qsub to run this job
# dir_main='/cbica/home/mayun/Projects/ABCD'
# qsub -terse -j y -pe threaded $1 -l h_vmem=10G -o $dir_main/Log/Log_workflow.log $dir_main/Script/workflow/workflow.sh

import os
import subprocess
import numpy as np
import time


workflow_step = ['raw2bids', 'fmriprep', 'xcpd']

dir_abcd_result = '/cbica/home/mayun/Projects/ABCD'

dir_script_cluster = os.path.join(dir_abcd_result, 'Script_Cluster')

N_process = 20

submit_command = 'qsub -terse -j y'
thread_command = '-pe threaded '
memory_command = '-l h_vmem='
log_command = '-o '

n_thread = 1
memory = '5G'

# find subject-session folders
list_subject_session = []
for root, dirs, files in os.walk(dir_script_cluster):
    # Add each subdirectory to the list
    for dir_name in dirs:
        if dir_name not in list_subject_session:
            list_subject_session.append(os.path.join(root, dir_name))

print(list_subject_session)
N_total_process = len(list_subject_session)
flag_process = np.zeros(N_total_process)

progress_running = 0
progress_count = 0
while progress_count < N_total_process:
    for i in range(N_total_process):
        if flag_process[i] == 0:
            file_bash = os.path.join(list_subject_session, 'workflow.sh')
            log_file = os.path.join(list_subject_session, 'Log_workflow.log')
            subprocess.run([submit_command, thread_command, n_thread, memory_command, memory, log_command, log_file, file_bash])
            flag_process[i] = 1
            progress_running += 1
            time.sleep(0.5)
            break

