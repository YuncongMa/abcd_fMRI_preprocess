# Yuncong Ma, 3/12/2024
# ABCD raw data to preprocessed data in a cluster environment
# This code does NOT work for DTI data
# source activate /cbica/home/mayun/.conda/envs/abcd
# python /cbica/home/mayun/Projects/ABCD/Script/abcd_fmri_preprocess_cluster.py
# python abcd_fmri_preprocess_cluster.py


# packages
import glob
import os
import shutil
import subprocess
from datetime import datetime
import numpy as np
import sys

# ========== settings ========== #
# setting for the cluster environment and conda
submit_command = 'qsub -terse -j y'
thread_command = '-pe threaded '
memory_command = '-l h_vmem='
log_command = '-o '

# settings for batch processing
n_subject_per_batch = 20
flag_clean_temp = 1
flag_clean_bids = 1
flag_clean_fmriprep = 1

# Test mode on local computer
flag_cluster = 1

# setup the directory of the pNet toolbox folder
if flag_cluster:
    dir_script = '/cbica/home/mayun/Projects/ABCD/Script'
    dir_python = '~/.conda/envs/abcd/bin/python'
    sys.path.append(dir_script)
    dir_abcd_test = os.path.dirname(dir_script)
    dir_fsl = '/cbica/software/external/fsl/centos7/5.0.11'
    dir_conda_env = '/cbica/home/mayun/.conda/envs/abcd'
else:
    dir_script = os.path.dirname(os.path.abspath(__name__))
    dir_abcd_test = os.path.dirname(dir_script)
    dir_fsl = '/usr/local/fsl'
    dir_conda_env = '/Users/yuncongma/anaconda3/envs/abcd_fmri'


# directories of sub-scripts
dir_abcd_raw2bids = os.path.join(dir_script, 'abcd_raw2bids')
dir_abcd2bids = os.path.join(dir_script, 'abcd_raw2bids', 'abcd-dicom2bids')

# bash script templates
file_template_raw2bids = os.path.join(dir_script, 'template', 'template_raw2bids.sh')
file_template_fmriprep = os.path.join(dir_script, 'template', 'template_fmriprep.sh')
file_template_xcpd = os.path.join(dir_script, 'template', 'template_xcpd.sh')
file_template_collect = os.path.join(dir_script, 'template', 'template_collect.sh')
if flag_cluster:
    file_template_workflow = os.path.join(dir_script, 'template', 'template_workflow_cluster.sh')
else:
    file_template_workflow = os.path.join(dir_script, 'template', 'template_workflow.sh')
file_template_report = os.path.join(dir_script, 'template', 'template_report.html')

# directories of raw data and folders for different steps in preprocessing
# raw data
dir_raw_data = os.path.join(dir_abcd_test, 'Example_Data')
# temporary folders for BIDS
dir_bids = os.path.join(dir_abcd_test, 'BIDS')
dir_bids_temp = os.path.join(dir_abcd_test, 'BIDS_Temp')
dir_fmriprep = os.path.join(dir_abcd_test, 'fmriprep')
dir_fmriprep_work = os.path.join(dir_abcd_test, 'fmriprep_work')
dir_xcpd = os.path.join(dir_abcd_test, 'XCP_D')
dir_xcpd_cifti = os.path.join(dir_abcd_test, 'XCP_D_cifti')
dir_xcpd_work = os.path.join(dir_abcd_test, 'XCP_D_work')

# directory to save scripts for cluster
dir_script_cluster = os.path.join(dir_abcd_test, 'Script_Cluster')

# singularity images for fmriprep and xcp-d
file_fmriprep = os.path.join(dir_abcd_test, 'Tool', 'nipreps_fmriprep_23.0.2.simg')
file_xcpd = os.path.join(dir_abcd_test, 'Tool', 'xcp_d-0.6.2.simg')

# setting for fmriprep
file_fs_license = os.path.join(dir_abcd_test, 'Tool/freesurfer/license.txt')
n_dummy = 10
fmriprep_output_space = 'MNI152NLin6Asym:res-2'
# setting for xcpd
n_dummy = 10
fwhm = 4.8
confound = '36P'
bp_low = 0.01
bp_high = 0.1
bp_order = 4
fd_threshold = 0.2

# final output
dir_failed = os.path.join(dir_abcd_test, 'Failed')
dir_result = os.path.join(dir_abcd_test, 'Result')

# steps to run
# ['raw2bids', 'fmriprep', 'xcpd', 'collect']
list_step=['fmriprep', 'xcpd']
# ============================================== #

# ======= start to extract raw data info ======= #
print(f"Start to extract scan info from raw data folder {dir_raw_data}")
# create folders
if not os.path.exists(dir_bids):
    os.makedirs(dir_bids)
# copy BIDS description file
shutil.copyfile(os.path.join(dir_abcd_raw2bids, 'dataset_description.json'), os.path.join(dir_bids, 'dataset_description.json'))
if not os.path.exists(dir_bids_temp):
    os.makedirs(dir_bids_temp)
if not os.path.exists(dir_script_cluster):
    os.makedirs(dir_script_cluster)
if not os.path.exists(dir_xcpd):
    os.makedirs(dir_xcpd)
if not os.path.exists(dir_xcpd_cifti):
    os.makedirs(dir_xcpd_cifti)
if not os.path.exists(dir_xcpd_work):
    os.makedirs(dir_xcpd_work)

# copy BIDS description file
shutil.copyfile(os.path.join(dir_abcd_raw2bids, 'dataset_description.json'),
                os.path.join(dir_bids, 'dataset_description.json'))

# extract information of tgz files, subject and session
list_file = []
list_sub = []
list_session = []
for root, dirs, files in os.walk(dir_raw_data):
    for filename in files:
        if filename.endswith(".tgz") and filename.__contains__("baselineYear1Arm1"):
            Keywords = filename.split('_')
            SUB = 'sub-' + Keywords[0]
            session = 'ses-' + Keywords[1]
            list_file.append(os.path.join(root, filename))
            list_sub.append(SUB)
            list_session.append(session)

subject_unique = np.unique(np.array(list_sub))
print(f'Found {len(subject_unique)} subjects and {len(list_file)} scans\n')


# ============================================== #

def keyword_in_string(keywords, text):
    for keyword in keywords:
        if keyword in text:
            return True
    return False


# ========== start to prepare scripts ========== #
print(f"Start to generate scripts in folder {dir_script_cluster}")
# Generate bash scripts
for _, subject in enumerate(subject_unique):
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

    # get session info
    indexes = [index for index, value in enumerate(list_sub) if value == subject]
    session = list_session[indexes[0]]

    # make subject-session directory for cluster script
    if not os.path.exists(os.path.join(dir_script_cluster, subject + '_' + session)):
        os.makedirs(os.path.join(dir_script_cluster, subject + '_' + session))

    dir_temp_sub = os.path.join(dir_bids_temp, subject + '_' + session)

    # Unpack/setup the data for this subject/session
    # only copy anat and rsfMRI data
    Keywords = ['ABCD-T1', 'ABCD-T2', 'FM', 'ABCD-rsfMRI']
    # generate a scan file
    list_sub_scan = os.path.join(dir_script_cluster, subject + '_' + session, 'List_Scan.txt')
    list_sub_scan = open(list_sub_scan, 'w')
    for _, i in enumerate(indexes):
        if keyword_in_string(Keywords, list_file[i]):
            print(list_file[i], file=list_sub_scan)
    list_sub_scan.close()

    # ====== workflow
    n_thread = 1
    memory = '5G'
    file_bash = os.path.join(dir_script_cluster, subject + '_' + session, 'workflow.sh')
    logFile = os.path.join(dir_script_cluster, subject + '_' + session, 'Log_workflow.log')
    with open(file_template_workflow, 'r') as file:
        workflow_content = file.read()
    workflow_content = workflow_content \
        .replace('{$date_time$}', str(date_time)) \
        .replace('{$job_submit_command_raw2bids$}', f'bash {file_bash}') \
        .replace('{$subject$}', subject[4:]) \
        .replace('{$session$}', session[4:]) \
        .replace('{$dir_script_sub$}', os.path.join(dir_script_cluster, subject + '_' + session)) \
        .replace('{$dir_bids_temp_sub$}', os.path.join(dir_bids_temp, subject + '_' + session)) \
        .replace('{$dir_fmriprep_temp_sub$}', os.path.join(dir_fmriprep_work, subject + '_' + session)) \
        .replace('{$dir_xcpd_temp_sub$}', os.path.join(dir_xcpd_work, subject + '_' + session))
    if flag_cluster:
        workflow_content = workflow_content \
            .replace('{$job_submit_command$}', f'{submit_command} {thread_command}{n_thread} {memory_command}{memory} {log_command}{logFile} {file_bash}')
    else:
        workflow_content = workflow_content \
            .replace('{$job_submit_command$}', f'bash {file_bash}')
    # check steps
    if 'raw2bids' in list_step:
        workflow_content = workflow_content.replace('{$run_raw2bids$}', '1')
    else:
        workflow_content = workflow_content.replace('{$run_raw2bids$}', '0')
    if 'fmriprep' in list_step:
        workflow_content = workflow_content.replace('{$run_fmriprep$}', '1')
    else:
        workflow_content = workflow_content.replace('{$run_fmriprep$}', '0')
    if 'xcpd' in list_step:
        workflow_content = workflow_content.replace('{$run_xcpd$}', '1')
    else:
        workflow_content = workflow_content.replace('{$run_xcpd$}', '0')
    if 'collect' in list_step:
        workflow_content = workflow_content.replace('{$run_collect$}', '1')
    else:
        workflow_content = workflow_content.replace('{$run_collect$}', '0')

    # ====== step 1: raw data to BIDS
    n_thread = 4
    memory = '10G'
    file_bash = os.path.join(dir_script_cluster, subject + '_' + session, 'raw2bids.sh')
    logFile = os.path.join(dir_script_cluster, subject + '_' + session, 'Log_raw2bids.log')
    file_raw2bids = os.path.join(dir_abcd_raw2bids, 'abcd_raw2bids.sh')
    if flag_cluster:
        workflow_content = workflow_content \
            .replace('{$job_submit_command_raw2bids$}',
                     f'{submit_command} {thread_command}{n_thread} {memory_command}{memory} {log_command}{logFile} {file_bash}')
    else:
        workflow_content = workflow_content \
            .replace('{$job_submit_command_raw2bids$}',
                     f'bash {file_bash}')
    with open(file_template_raw2bids, 'r') as file:
        template_content = file.read()
    template_content = template_content \
        .replace('{$date_time$}', str(date_time)) \
        .replace('{$job_submit_command$}',
                 f'{submit_command} {thread_command}{n_thread} {memory_command}{memory} {log_command}{logFile} {file_bash}') \
        .replace('{$dir_conda_env$}', dir_conda_env) \
        .replace('{$file_raw2bids$}', file_raw2bids) \
        .replace('{$subject$}', subject[4:]) \
        .replace('{$session$}', session[4:]) \
        .replace('{$dir_abcd2bids$}', dir_abcd2bids) \
        .replace('{$dir_bids$}', dir_bids) \
        .replace('{$dir_temp_sub$}', dir_temp_sub) \
        .replace('{$dir_abcd_raw2bids$}', dir_abcd_raw2bids) \
        .replace('{$list_sub_scan$}', list_sub_scan.name) \
        .replace('{$file_log$}', logFile)

    file_bash = open(file_bash, 'w')
    print(template_content, file=file_bash)
    file_bash.close()

    # ====== step 2: fmriprep
    n_thread = 4
    memory = '48G'
    memory_fmriprep = 47000
    file_bash = os.path.join(dir_script_cluster, subject + '_' + session, 'fmriprep.sh')
    logFile = os.path.join(dir_script_cluster, subject + '_' + session, 'Log_fmriprep.log')
    dir_fmriprep_work_sub = os.path.join(dir_fmriprep_work, subject + '_' + session)
    if flag_cluster:
        workflow_content = workflow_content \
            .replace('{$job_submit_command_fmriprep$}',
                     f'{submit_command} {thread_command}{n_thread} {memory_command}{memory} {log_command}{logFile} {file_bash}')
    else:
        workflow_content = workflow_content \
            .replace('{$job_submit_command_fmriprep$}',
                     f'bash {file_bash}')
    with open(file_template_fmriprep, 'r') as file:
        template_content = file.read()
    template_content = template_content \
        .replace('{$date_time$}', str(date_time)) \
        .replace('{$job_submit_command$}',
                 f'{submit_command} {thread_command}{n_thread} {memory_command}{memory} {log_command}{logFile} {file_bash}') \
        .replace('{$file_fmriprep$}', file_fmriprep) \
        .replace('{$dir_bids$}', dir_bids) \
        .replace('{$dir_fmriprep$}', dir_fmriprep) \
        .replace('{$n_thread$}', str(n_thread)) \
        .replace('{$max_mem$}', str(memory_fmriprep)) \
        .replace('{$file_fs_license$}', file_fs_license) \
        .replace('{$n_dummy$}', str(n_dummy)) \
        .replace('{$dir_fmriprep_work_sub$}', dir_fmriprep_work_sub) \
        .replace('{$subject$}', subject[4:]) \
        .replace('{$output_space$}', fmriprep_output_space) \
        .replace('{$file_log$}', logFile)

    file_bash = open(file_bash, 'w')
    print(template_content, file=file_bash)
    file_bash.close()

    # ====== step 3: XCP-D
    n_thread = 4
    memory = '11G'
    memory_xcpd = 10
    file_bash = os.path.join(dir_script_cluster, subject + '_' + session, 'xcpd.sh')
    logFile = os.path.join(dir_script_cluster, subject + '_' + session, 'Log_xcpd.log')
    dir_xcpd_work_sub = os.path.join(dir_xcpd_work, subject + '_' + session)
    if flag_cluster:
        workflow_content = workflow_content \
            .replace('{$job_submit_command_xcpd$}',
                     f'{submit_command} {thread_command}{n_thread} {memory_command}{memory} {log_command}{logFile} {file_bash}')
    else:
        workflow_content = workflow_content \
            .replace('{$job_submit_command_xcpd$}',
                     f'bash {file_bash}')
    with open(file_template_xcpd, 'r') as file:
        template_content = file.read()
    template_content = template_content \
        .replace('{$date_time$}', str(date_time)) \
        .replace('{$job_submit_command$}',
                 f'{submit_command} {thread_command}{n_thread} {memory_command}{memory} {log_command}{logFile} {file_bash}') \
        .replace('{$file_xcpd$}', file_xcpd) \
        .replace('{$dir_xcpd$}', dir_xcpd) \
        .replace('{$dir_xcpd_cifti$}', dir_xcpd_cifti) \
        .replace('{$dir_fmriprep$}', dir_fmriprep) \
        .replace('{$n_thread$}', str(n_thread)) \
        .replace('{$memory$}', str(memory_xcpd)) \
        .replace('{$subject$}', subject[4:]) \
        .replace('{$file_fs_license$}', file_fs_license) \
        .replace('{$n_dummy$}', str(n_dummy)) \
        .replace('{$fwhm$}', str(fwhm)) \
        .replace('{$confound$}', confound) \
        .replace('{$bp_low$}', str(bp_low)) \
        .replace('{$bp_high$}', str(bp_high)) \
        .replace('{$bp_order$}', str(bp_order)) \
        .replace('{$fd_threshold$}', str(fd_threshold)) \
        .replace('{$dir_xcpd_work_sub$}', dir_xcpd_work_sub) \
        .replace('{$file_log$}', logFile)

    file_bash = open(file_bash, 'w')
    print(template_content, file=file_bash)
    file_bash.close()

    # ====== step 4: collect
    # Move results into result folder or failed folder
    # Generate HTML-based report files for manual examination
    n_thread = 1
    memory = '5G'
    file_bash = os.path.join(dir_script_cluster, subject + '_' + session, 'collect.sh')
    logFile = os.path.join(dir_script_cluster, subject + '_' + session, 'Log_collect.log')
    if flag_cluster:
        workflow_content = workflow_content \
            .replace('{$job_submit_command_collect$}',
                     f'{submit_command} {thread_command}{n_thread} {memory_command}{memory} {log_command}{logFile} {file_bash}')
    else:
        workflow_content = workflow_content \
            .replace('{$job_submit_command_collect$}',
                     f'bash {file_bash}')
    with open(file_template_collect, 'r') as file:
        template_content = file.read()
    template_content = template_content \
        .replace('{$date_time$}', str(date_time)) \
        .replace('{$job_submit_command$}',
                 f'{submit_command} {thread_command}{n_thread} {memory_command}{memory} {log_command}{logFile} {file_bash}') \
        .replace('{$subject$}', subject[4:]) \
        .replace('{$session$}', session[4:]) \
        .replace('{$dir_failed$}', dir_failed) \
        .replace('{$dir_result$}', dir_result) \
        .replace('{$file_template$}', file_template_report) \
        .replace('{$dir_bids$}', dir_bids) \
        .replace('{$dir_bids_temp$}', dir_bids_temp) \
        .replace('{$dir_fmriprep$}', dir_fmriprep) \
        .replace('{$dir_fmriprep_work_sub$}', dir_fmriprep_work_sub) \
        .replace('{$dir_xcpd$}', dir_xcpd) \
        .replace('{$dir_xcpd_cifti$}', dir_xcpd_cifti) \
        .replace('{$dir_xcpd_work_sub$}', dir_xcpd_work_sub)

    file_bash = open(file_bash, 'w')
    print(template_content, file=file_bash)
    file_bash.close()

    # output workflow.sh
    file_bash = os.path.join(dir_script_cluster, subject + '_' + session, 'workflow.sh')
    file_bash = open(file_bash, 'w')
    print(workflow_content, file=file_bash)
    file_bash.close()

print(f"All scripts are generated successfully\n")
# ============================================== #

# ============= start run workflow ============ #
file_bash = os.path.join(dir_script, 'workflow', 'workflow_cluster.sh')
logFile = os.path.join(dir_abcd_test, 'Log', 'Log_workflow_cluster.log')
n_thread = 1
memory = '5G'
maxProgress=20  # 20 max workflows
minSpace=500  # 500GB free space at least to submit new jobs
submit_command = ['qsub', '-terse', '-j', 'y', '-pe', 'threaded', str(n_thread), '-l', 'h_vmem='+memory, '-o', logFile, file_bash, 
                  '--main', dir_abcd_test, '--scriptCluster', dir_script_cluster, '--maxProgress', str(maxProgress), '--minSpace', str(minSpace)]
subprocess.run(submit_command)

print(f"workflow job is submitted\n")
# ============================================== #
