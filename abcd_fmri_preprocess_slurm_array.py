# Yuncong Ma, 5/10/2024
# This script is to preprocess ABCD fMRI data in ABCD group project
# This code does NOT work for DTI data
# This script will submit a workflow_cluster.sh job using SLURM array job
#
#
# command code to run in a cluster environment
# source activate /cbica/home/mayun/.conda/envs/abcd
# python /cbica/home/mayun/Projects/ABCD/Script/abcd_fmri_preprocess_slurm_array.py


# packages
import glob
import os
import shutil
import subprocess
from datetime import datetime
import numpy as np
import sys

# ========== settings ========== #

# Test mode on local computer
flag_cluster = 1
# whether to skip finished jobs
flag_continue = 1

# directories to raw data and result
# setup the directory of the pNet toolbox folder
dir_script = os.path.dirname(os.path.abspath(__file__))
dir_python = '/cbica/projects/ABCD_PreProc/.conda/envs/abcd/bin/python'
sys.path.append(dir_script)

# dir_raw_data = '/cbica/projects/ABCD_Data_Releases/Data/image03'
dir_raw_data = '/cbica/home/mayun/Projects/ABCD/Example_Data'
    
dir_abcd_result = os.path.dirname(dir_script)

dir_fsl = '/cbica/software/external/fsl/centos7/5.0.11'
dir_conda_env = '/cbica/projects/ABCD_PreProc/.conda/envs/abcd'

# setting for SGE array job
# array job name
name_array_job = 'ABCD'
# max number of concurrent workflow jobs
max_workflow = 100

# steps to run
default_step = ['raw2bids', 'bids_qc', 'fmriprep', 'xcpd', 'collect']
list_step = ['raw2bids', 'bids_qc', 'fmriprep', 'xcpd', 'collect']

# singularity images for dcm2bids, fmriprep and xcp-d
file_dcm2bids = os.path.join(dir_abcd_result, 'Tool', 'dcm2bids.simg')
file_fmriprep = os.path.join(dir_abcd_result, 'Tool', 'nipreps_fmriprep_23.2.1.simg')
file_xcpd = os.path.join(dir_abcd_result, 'Tool', 'xcp_d-0.6.2.simg')

# setting for the cluster environment and conda
submit_command = 'sbatch --parsable'
time_command = '#SBATCH --time={$max_time$}'
thread_command = '#SBATCH --cpus-per-task={$n_thread$}'
memory_command = '#SBATCH --mem={$memory$}'
log_command = '#SBATCH -o {$logFile$}'
hold_command = '--dependency=afterok:'

# directories of sub-scripts in toolbox abcd_fmri_preprocess
dir_abcd_raw2bids = os.path.join(dir_script, 'abcd_raw2bids')
dir_abcd2bids = os.path.join(dir_script, 'abcd_raw2bids', 'abcd-dicom2bids')

# bash script templates in /template
file_template_workflow_cluster = os.path.join(dir_script, 'template', 'template_workflow_cluster.sh')
file_template_submit_sge_array = os.path.join(dir_script, 'template', 'template_submit_sge_array.sh')
file_template_sge_array = os.path.join(dir_script, 'template', 'template_sge_array.sge')
file_template_raw2bids = os.path.join(dir_script, 'template', 'template_raw2bids.sh')
file_template_qc_bids = os.path.join(dir_script, 'template', 'template_bids_qc.sh')
file_template_fmriprep = os.path.join(dir_script, 'template', 'template_fmriprep.sh')
file_template_xcpd = os.path.join(dir_script, 'template', 'template_xcpd.sh')
file_template_collect = os.path.join(dir_script, 'template', 'template_collect.sh')
file_template_workflow = os.path.join(dir_script, 'template', 'template_slurm_workflow_sub.sh')
file_template_report = os.path.join(dir_script, 'template', 'template_report.html')

# python script
python_bids_filter = os.path.join(dir_script, 'quality_control', 'bids_filter.py')

# directories of folders for different steps in preprocessing
# temporary folders for BIDS
dir_bids = os.path.join(dir_abcd_result, 'BIDS')
dir_bids_work = os.path.join(dir_abcd_result, 'BIDS_Temp')
dir_bids_qc = os.path.join(dir_abcd_result, 'BIDS_QC')
dir_fmriprep = os.path.join(dir_abcd_result, 'fmriprep')
dir_fmriprep_work = os.path.join(dir_abcd_result, 'fmriprep_work')
dir_xcpd = os.path.join(dir_abcd_result, 'XCP_D')
dir_xcpd_cifti = os.path.join(dir_abcd_result, 'XCP_D_cifti')
dir_xcpd_work = os.path.join(dir_abcd_result, 'XCP_D_work')
dir_log = os.path.join(dir_abcd_result, 'Log')
dir_dataset_info = os.path.join(dir_abcd_result, 'Dataset_Info')

# directory to save scripts for cluster
dir_script_cluster = os.path.join(dir_abcd_result, 'Script_Cluster')

# final output
dir_failed = os.path.join(dir_abcd_result, 'Failed')
dir_result = os.path.join(dir_abcd_result, 'Result')

# setting for fmriprep
file_fs_license = os.path.join(dir_abcd_result, 'Tool/freesurfer/license.txt')
n_dummy = 10
fmriprep_output_space = 'MNI152NLin6Asym:res-2'
# setting for xcpd
n_dummy = 0
fwhm = 6
confound = '36P'
bp_low = 0.01
bp_high = 0.1
bp_order = 4
fd_threshold = 0.2

# ============================================== #

# creat folders and check its existence
def make_folder(dir_folder: str):
    if not os.path.exists(dir_folder):
        os.makedirs(dir_folder)
    if not os.path.isdir(dir_folder):
        raise ValueError('Failed in creating directory: '+dir_folder)
    
def check_folder(dir_folder: str):
    if not os.path.isdir(dir_folder):
        raise ValueError('Non-existed directory: '+dir_folder)

# check file existence
def check_file(dir_file: str):
    if not os.path.isfile(dir_file):
        raise ValueError('Cannot find file: '+dir_file)

# ======= make folder and check file/dir existence ======= #
print(f"Start to make folders, check existence of directories and files")
# create folders
make_folder(dir_script_cluster)
make_folder(os.path.join(dir_script_cluster, 'log_array_job'))
make_folder(dir_log)
make_folder(dir_bids)
make_folder(dir_bids_work)
make_folder(dir_bids_qc)
make_folder(dir_xcpd)
make_folder(dir_xcpd_cifti)
make_folder(dir_xcpd_work)
make_folder(dir_result)
make_folder(dir_failed)
make_folder(dir_dataset_info)

# check file existence
# singularity images
check_file(file_dcm2bids)
check_file(file_fmriprep)
check_file(file_xcpd)
# freesurfer license
check_file(file_fs_license)
# fsl
check_folder(dir_fsl)
# conda
check_folder(dir_conda_env)
# script templates
check_file(file_template_workflow_cluster)
check_file(file_template_submit_sge_array)
check_file(file_template_sge_array)
check_file(file_template_raw2bids)
check_file(file_template_qc_bids)
check_file(file_template_fmriprep)
check_file(file_template_xcpd)
check_file(file_template_collect)
check_file(file_template_workflow)
# check_file(file_template_report)

# check toolbox directory existence
check_folder(dir_abcd_raw2bids)
check_folder(dir_abcd2bids)


# ======= start to extract raw data info ======= #
print(f"Start to extract scan info from raw data folder {dir_raw_data}")
# extract scan info if not exist
file_list_tgz = os.path.join(dir_dataset_info, 'List_tgz_example.txt')
if not os.path.isfile(file_list_tgz): 
    check_file(os.path.join(dir_script, 'workflow', 'extract_dataset_info.sh'))
    subprocess.run(['bash',os.path.join(dir_script, 'workflow', 'extract_dataset_info.sh'), '--raw', dir_raw_data, '--file-info', file_list_tgz])
    check_file(file_list_tgz)

list_tgz = []
file_list_tgz = open(file_list_tgz, 'r')
list_tgz = [line.replace('\n', '') for line in file_list_tgz.readlines()]
file_list_tgz.close
list_tgz = np.sort(np.array(list_tgz))
list_tgz_basename = [os.path.basename(file_abs) for _, file_abs in enumerate(list_tgz)]


# extract information of tgz files, subject and session
def keyword_in_string(keywords, text):
    for keyword in keywords:
        if keyword in text:
            return True
    return False

# select files matching keywords
Keywords_tgz = ['ABCD-T1', 'ABCD-T2', 'ABCD-fMRI-FM', 'ABCD-rsfMRI']
list_tgz_2 = []
list_tgz_basename_2 = []
for index, file_name in enumerate(list_tgz_basename):
    if "baselineYear1Arm1" in file_name and keyword_in_string(Keywords_tgz, file_name):
        list_tgz_2.append(list_tgz[index])
        list_tgz_basename_2.append(list_tgz_basename[index])
list_tgz = list_tgz_2
list_tgz_basename = list_tgz_basename_2

# extract sub-ses info and corresponding scan files
file_sub_ses = os.path.join(dir_dataset_info, 'List_Subject_Session_example.txt')
if not os.path.isfile(file_sub_ses): 
    list_file = []
    list_sub_ses = []
    for index, file_name in enumerate(list_tgz_basename):
        Keywords = file_name.split('_')
        subject = 'sub-' + Keywords[0]
        session = 'ses-' + Keywords[1]
        list_file.append(list_tgz[index])
        list_sub_ses.append(subject+'_'+session)
            
    list_sub_ses = np.unique(np.array(list_sub_ses))
    
    # output sub-sess
    file_sub_ses = open(file_sub_ses, 'w')
    for _, sub_ses in enumerate(list_sub_ses): 
        print(sub_ses, file=file_sub_ses)
    file_sub_ses.close
    check_file(file_sub_ses.name)
    
else:
    file_sub_ses = open(file_sub_ses, 'r')
    list_sub_ses = [line.replace('\n','') for line in file_sub_ses.readlines()]
    list_sub_ses = np.unique(np.array(list_sub_ses))
    file_sub_ses.close
    list_file = []
    for _, sub_ses in enumerate(list_sub_ses):
        Keywords = sub_ses.split('_')
        subject = Keywords[0].split('-')[1]
        session = Keywords[1].split('-')[1]
        for index, file_name in enumerate(list_tgz_basename):
            if subject in file_name and session in file_name:
                list_file.append(list_tgz[index])


print(f'Found {len(list_sub_ses)} subject_session and {len(list_file)} scans\n')

# output related scan directories
file_list_file = os.path.join(dir_dataset_info, 'List_file.txt')
file_list_file = open(file_list_file, 'w')
for _, file_abs in enumerate(list_file): 
    print(file_abs, file=file_list_file)
file_list_file.close
check_file(file_list_file.name)

# copy BIDS description file
check_file(os.path.join(dir_abcd_raw2bids, 'dataset_description.json'))
shutil.copyfile(os.path.join(dir_abcd_raw2bids, 'dataset_description.json'), os.path.join(dir_bids, 'dataset_description.json'))
check_file(os.path.join(dir_bids, 'dataset_description.json'))


# ============================================== #

now = datetime.now()
date_time = now.strftime("%m/%d/%Y, %H:%M")

# ======= SGE array job submission commands ====== #
file_array_job = os.path.join(dir_script_cluster, 'List_workflow_command.txt')
print(f"Start to generate array jobs submission commands in {file_array_job}")

file_array_job = open(file_array_job, 'w')
for _, sub_ses in enumerate(list_sub_ses):    
    bashFile = os.path.join(dir_script_cluster, sub_ses, 'workflow.sh')
    logFile = os.path.join(dir_script_cluster, sub_ses, 'Log_workflow.log')
    
    job_submit_command=f'bash {bashFile}'
    
    print(job_submit_command, file=file_array_job)
    
file_array_job.close

with open(file_template_submit_sge_array, 'r') as file:
        submit_sge_array = file.read()
file_submit_sge_array = os.path.join(dir_script_cluster, 'submit_slurm_array.sh')
file_submit_array_job = os.path.join(dir_script_cluster, 'slurm_array.sge')
n_thread = 1
memory = '1G'
max_time = '24:00:00'
slurm_option = thread_command.replace('{$n_thread$}', str(n_thread)) + '\n' + \
        memory_command.replace('{$memory$}', str(memory)) + '\n' + \
        time_command.replace('{$max_time$}', max_time) + '\n' + \
        log_command.replace('{$logFile$}', logFile)
submit_sge_array = submit_sge_array \
        .replace('#{$job_setting$}',slurm_option) \
        .replace('{$date_time$}', str(date_time)) \
        .replace('{$dir_script_cluster$}', dir_script_cluster) \
        .replace('{$file_submit_sge_array$}', file_submit_sge_array) \
        .replace('{$submit_command$}', f'{submit_command} {file_submit_array_job}') 
file_submit_sge_array = open(file_submit_sge_array, 'w')
print(submit_sge_array, file=file_submit_sge_array)
file_submit_sge_array.close

with open(file_template_sge_array, 'r') as file:
        sge_array = file.read()
sge_array = sge_array \
        .replace('{$date_time$}', str(date_time)) \
        .replace('{$name_array_job$}', name_array_job) \
        .replace('{$N$}', str(len(list_sub_ses))) \
        .replace('{$max_workflow$}', str(max_workflow)) \
        .replace('{$dir_script_cluster$}', dir_script_cluster) \
        .replace('{$file_array_job$}', file_array_job.name)
file_submit_array_job = open(file_submit_array_job, 'w')
print(sge_array, file=file_submit_array_job)
file_submit_array_job.close


# ========== start to prepare scripts ========== #
print(f"Start to generate scripts in folder {dir_script_cluster}")

# Generate bash scripts for each subject and session
for _, sub_ses in enumerate(list_sub_ses):
    Keywords = sub_ses.split('_')
    subject = Keywords[0]  # sub-*
    sesssion = Keywords[1]  # ses-*
    subjectID = subject.split('-')[1]
    sessionID = sesssion.split('-')[1]

    # get file indexes
    indexes = [index for index, file_name in enumerate(list_file) if subjectID in file_name and sessionID in file_name]

    # make subject-session directory for cluster script
    if not os.path.exists(os.path.join(dir_script_cluster, sub_ses)):
        os.makedirs(os.path.join(dir_script_cluster, sub_ses))

    dir_temp_sub = os.path.join(dir_bids_work, sub_ses)

    # Unpack/setup the data for this subject/session
    # generate a scan file
    list_sub_scan = os.path.join(dir_script_cluster, sub_ses, 'List_Scan.txt')
    list_sub_scan = open(list_sub_scan, 'w')
    flag_NORM = 0
    for _, i in enumerate(indexes):
        if "T1-NORM" in list_file[i] or "T2-NORM" in list_file[i]:
            flag_NORM = 1
            break
    if flag_NORM == 0:
        # use all
        for _, i in enumerate(indexes):
            print(list_file[i], file=list_sub_scan)
    else:
        # use T1-NORM instead of T1, use T2-NORM instead of T2
        for _, i in enumerate(indexes):
            if 'ABCD-T1' in list_file[i]:
                if 'ABCD-T1-NORM' in list_file[i]:
                    print(list_file[i], file=list_sub_scan)
            elif 'ABCD-T2' in list_file[i]:
                if 'ABCD-T2-NORM' in list_file[i]:
                    print(list_file[i], file=list_sub_scan)
            else:
                print(list_file[i], file=list_sub_scan)
                
    list_sub_scan.close()

    # ====== workflow
    n_thread = 1
    memory = '1G'
    max_time = '24:00:00'
    file_bash = os.path.join(dir_script_cluster, sub_ses, 'workflow.sh')
    logFile = os.path.join(dir_script_cluster, sub_ses, 'Log_workflow.log')
    if os.path.exists(logFile):
        subprocess.run(['rm','-rf',logFile])
    with open(file_template_workflow, 'r') as file:
        workflow_content = file.read()
    slurm_option = thread_command.replace('{$n_thread$}', str(n_thread)) + '\n' + \
        memory_command.replace('{$memory$}', str(memory)) + '\n' + \
        time_command.replace('{$max_time$}', max_time) + '\n' + \
        log_command.replace('{$logFile$}', logFile)
    workflow_content = workflow_content \
        .replace('#{$job_setting$}', slurm_option) \
        .replace('{$date_time$}', str(date_time)) \
        .replace('{$subject$}', subjectID) \
        .replace('{$session$}', sessionID) \
        .replace('{$dir_script_cluster$}', dir_script_cluster) \
        .replace('{$dir_bids_work$}', dir_bids_work) \
        .replace('{$dir_fmriprep_work$}', dir_fmriprep_work) \
        .replace('{$dir_xcpd_work$}', dir_xcpd_work)
    if flag_cluster:
        workflow_content = workflow_content \
            .replace('{$job_submit_command$}', f'{submit_command} {file_bash}')
    else:
        workflow_content = workflow_content \
            .replace('{$job_submit_command$}', f'bash {file_bash}')
            
    # check steps
    for _, step_name in enumerate(default_step):
        if step_name in list_step:
            workflow_content = workflow_content.replace('{$run_'+step_name+'$}', '1')
        else:
            workflow_content = workflow_content.replace('{$run_'+step_name+'$}', '0')
            
    # last job for SGE to hold jobs
    lastJob = ''
            
    # ====== step 1: raw data to BIDS
    n_thread = 4
    memory = '10G'
    max_time = '2:00:00'
    file_bash = os.path.join(dir_script_cluster, sub_ses, 'raw2bids.sh')
    logFile = os.path.join(dir_script_cluster, sub_ses, 'Log_raw2bids.log')
    file_raw2bids = os.path.join(dir_abcd_raw2bids, 'abcd_raw2bids.sh')
    if flag_cluster:
        if len(lastJob) == 0:
            workflow_content = workflow_content \
                .replace('{$job_submit_command_raw2bids$}',
                     f'{submit_command} {file_bash}')
        else:
            workflow_content = workflow_content \
                .replace('{$job_submit_command_raw2bids$}',
                     f'{submit_command} {hold_command}{lastJob} {file_bash}')
    else:
        workflow_content = workflow_content \
            .replace('{$job_submit_command_raw2bids$}',
                     f'bash {file_bash}')
    if 'raw2bids' in list_step:
        lastJob = file_bash
    with open(file_template_raw2bids, 'r') as file:
        template_content = file.read()
    slurm_option = thread_command.replace('{$n_thread$}', str(n_thread)) + '\n' + \
        memory_command.replace('{$memory$}', str(memory)) + '\n' + \
        time_command.replace('{$max_time$}', max_time) + '\n' + \
        log_command.replace('{$logFile$}', logFile)
    template_content = template_content \
        .replace('#{$job_setting$}', slurm_option) \
        .replace('{$date_time$}', str(date_time)) \
        .replace('{$job_submit_command$}',
                 f'{submit_command} {file_bash}') \
        .replace('{$dir_conda_env$}', dir_conda_env) \
        .replace('{$file_raw2bids$}', file_raw2bids) \
        .replace('{$subject$}', subjectID) \
        .replace('{$session$}', sessionID) \
        .replace('{$dir_abcd2bids$}', dir_abcd2bids) \
        .replace('{$file_dcm2bids$}', file_dcm2bids) \
        .replace('{$dir_bids$}', dir_bids) \
        .replace('{$dir_bids_work$}', dir_bids_work) \
        .replace('{$dir_abcd_raw2bids$}', dir_abcd_raw2bids) \
        .replace('{$list_sub_scan$}', list_sub_scan.name) \
        .replace('{$file_log$}', logFile)

    file_bash = open(file_bash, 'w')
    print(template_content, file=file_bash)
    file_bash.close()

    # ====== step 2: qc on BIDS
    n_thread = 4
    memory = '10G'
    file_bash = os.path.join(dir_script_cluster, sub_ses, 'bids_qc.sh')
    logFile = os.path.join(dir_script_cluster, sub_ses, 'Log_bids_qc.log')
    file_qc_bids = os.path.join(dir_script, 'quality_control', 'qc_bids.py')
    if flag_cluster:
        if len(lastJob) == 0:
            workflow_content = workflow_content \
                .replace('{$job_submit_command_bids_qc$}',
                     f'{submit_command} {file_bash}')
        else:
            workflow_content = workflow_content \
                .replace('{$job_submit_command_bids_qc$}',
                     f'{submit_command} {hold_command}$lastJob {file_bash}')
    else:
        workflow_content = workflow_content \
            .replace('{$job_submit_command_bids_qc$}',
                     f'bash {file_bash}')
    if 'bids_qc' in list_step:
        lastJob = file_bash
    with open(file_template_qc_bids, 'r') as file:
        template_content = file.read()
    slurm_option = thread_command.replace('{$n_thread$}', str(n_thread)) + '\n' + \
        memory_command.replace('{$memory$}', str(memory)) + '\n' + \
        time_command.replace('{$max_time$}', max_time) + '\n' + \
        log_command.replace('{$logFile$}', logFile)
    template_content = template_content \
        .replace('#{$job_setting$}', slurm_option) \
        .replace('{$date_time$}', str(date_time)) \
        .replace('{$job_submit_command$}',
                 f'{submit_command} {file_bash}') \
        .replace('{$dir_conda_env$}', dir_conda_env) \
        .replace('{$file_qc_bids$}', file_qc_bids) \
        .replace('{$subject$}', subjectID) \
        .replace('{$session$}', sessionID) \
        .replace('{$dir_bids$}', dir_bids) \
        .replace('{$dir_bids_qc$}', dir_bids_qc) \
        .replace('{$file_log$}', logFile)

    file_bash = open(file_bash, 'w')
    print(template_content, file=file_bash)
    file_bash.close()

    # ====== step 3: fmriprep
    n_thread = 8
    memory = '48G'
    memory_fmriprep = 47000
    max_time = '24:00:00'
    file_bash = os.path.join(dir_script_cluster, sub_ses, 'fmriprep.sh')
    logFile = os.path.join(dir_script_cluster, sub_ses, 'Log_fmriprep.log')
    if flag_cluster:
        if len(lastJob) == 0:
            workflow_content = workflow_content \
                .replace('{$job_submit_command_fmriprep$}',
                     f'{submit_command} {file_bash}')
        else:
            workflow_content = workflow_content \
                .replace('{$job_submit_command_fmriprep$}',
                     f'{submit_command} {hold_command}$lastJob {file_bash}')
    else:
        workflow_content = workflow_content \
            .replace('{$job_submit_command_fmriprep$}',
                     f'bash {file_bash}')
    if 'fmriprep' in list_step:
        lastJob = file_bash
    with open(file_template_fmriprep, 'r') as file:
        template_content = file.read()
    slurm_option = thread_command.replace('{$n_thread$}', str(n_thread)) + '\n' + \
        memory_command.replace('{$memory$}', str(memory)) + '\n' + \
        time_command.replace('{$max_time$}', max_time) + '\n' + \
        log_command.replace('{$logFile$}', logFile)
    template_content = template_content \
        .replace('#{$job_setting$}', slurm_option) \
        .replace('{$job_submit_command$}',
                 f'{submit_command} {file_bash}') \
        .replace('{$file_fmriprep$}', file_fmriprep) \
        .replace('{$dir_bids$}', dir_bids) \
        .replace('{$dir_bids_qc$}', dir_bids_qc) \
        .replace('{$dir_conda_env$}', dir_conda_env) \
        .replace('{$python_bids_filter$}', python_bids_filter) \
        .replace('{$dir_fmriprep$}', dir_fmriprep) \
        .replace('{$n_thread$}', str(n_thread)) \
        .replace('{$max_mem$}', str(memory_fmriprep)) \
        .replace('{$file_fs_license$}', file_fs_license) \
        .replace('{$n_dummy$}', str(n_dummy)) \
        .replace('{$dir_fmriprep_work$}', dir_fmriprep_work) \
        .replace('{$subject$}', subjectID) \
        .replace('{$session$}', sessionID) \
        .replace('{$output_space$}', fmriprep_output_space) \
        .replace('{$file_log$}', logFile)

    file_bash = open(file_bash, 'w')
    print(template_content, file=file_bash)
    file_bash.close()

    # ====== step 4: XCP-D
    n_thread = 8
    memory = '21G'
    memory_xcpd = 20
    max_time = '2:0:0'
    file_bash = os.path.join(dir_script_cluster, sub_ses, 'xcpd.sh')
    logFile = os.path.join(dir_script_cluster, sub_ses, 'Log_xcpd.log')
    if flag_cluster:
        if len(lastJob) == 0:
            workflow_content = workflow_content \
                .replace('{$job_submit_command_xcpd$}',
                     f'{submit_command} {file_bash}')
        else:
            workflow_content = workflow_content \
                .replace('{$job_submit_command_xcpd$}',
                     f'{submit_command} {hold_command}$lastJob {file_bash}')
    else:
        workflow_content = workflow_content \
            .replace('{$job_submit_command_xcpd$}',
                     f'bash {file_bash}')
    if 'xcpd' in list_step:
        lastJob = file_bash
    with open(file_template_xcpd, 'r') as file:
        template_content = file.read()
    slurm_option = thread_command.replace('{$n_thread$}', str(n_thread)) + '\n' + \
        memory_command.replace('{$memory$}', str(memory)) + '\n' + \
        time_command.replace('{$max_time$}', max_time) + '\n' + \
        log_command.replace('{$logFile$}', logFile)
    template_content = template_content \
        .replace('#{$job_setting$}', slurm_option) \
        .replace('{$date_time$}', str(date_time)) \
        .replace('{$job_submit_command$}',
                 f'{submit_command} {file_bash}') \
        .replace('{$file_xcpd$}', file_xcpd) \
        .replace('{$dir_xcpd$}', dir_xcpd) \
        .replace('{$dir_xcpd_cifti$}', dir_xcpd_cifti) \
        .replace('{$dir_fmriprep$}', dir_fmriprep) \
        .replace('{$n_thread$}', str(n_thread)) \
        .replace('{$memory$}', str(memory_xcpd)) \
        .replace('{$subject$}', subjectID) \
        .replace('{$session$}', sessionID) \
        .replace('{$file_fs_license$}', file_fs_license) \
        .replace('{$n_dummy$}', str(n_dummy)) \
        .replace('{$fwhm$}', str(fwhm)) \
        .replace('{$confound$}', confound) \
        .replace('{$bp_low$}', str(bp_low)) \
        .replace('{$bp_high$}', str(bp_high)) \
        .replace('{$bp_order$}', str(bp_order)) \
        .replace('{$fd_threshold$}', str(fd_threshold)) \
        .replace('{$dir_xcpd_work$}', dir_xcpd_work) \
        .replace('{$file_log$}', logFile)

    file_bash = open(file_bash, 'w')
    print(template_content, file=file_bash)
    file_bash.close()

    # ====== step 5: collect
    # Move results into result folder or failed folder
    # Generate HTML-based report files for manual examination
    n_thread = 1
    memory = '5G'
    max_time = '0:30:00'
    file_bash = os.path.join(dir_script_cluster, sub_ses, 'collect.sh')
    logFile = os.path.join(dir_script_cluster, sub_ses, 'Log_collect.log')
    if flag_cluster:
        if len(lastJob) == 0:
            workflow_content = workflow_content \
                .replace('{$job_submit_command_collect$}',
                     f'{submit_command} {file_bash}')
        else:
            workflow_content = workflow_content \
                .replace('{$job_submit_command_collect$}',
                     f'{submit_command} {hold_command}$lastJob {file_bash}')
    else:
        workflow_content = workflow_content \
            .replace('{$job_submit_command_collect$}',
                     f'bash {file_bash}')
    if 'collect' in list_step:
        lastJob = file_bash
    with open(file_template_collect, 'r') as file:
        template_content = file.read()
    slurm_option = thread_command.replace('{$n_thread$}', str(n_thread)) + '\n' + \
        memory_command.replace('{$memory$}', str(memory)) + '\n' + \
        time_command.replace('{$max_time$}', max_time) + '\n' + \
        log_command.replace('{$logFile$}', logFile)
    template_content = template_content \
        .replace('#{$job_setting$}', slurm_option) \
        .replace('{$date_time$}', str(date_time)) \
        .replace('{$job_submit_command$}',
                 f'{submit_command} {file_bash}') \
        .replace('{$subject$}', subjectID) \
        .replace('{$session$}', sessionID) \
        .replace('{$dir_script_cluster$}', dir_script_cluster) \
        .replace('{$dir_failed$}', dir_failed) \
        .replace('{$dir_result$}', dir_result) \
        .replace('{$file_template$}', file_template_report) \
        .replace('{$dir_bids$}', dir_bids) \
        .replace('{$dir_bids_work$}', dir_bids_work) \
        .replace('{$dir_bids_qc$}', dir_bids_qc) \
        .replace('{$dir_fmriprep$}', dir_fmriprep) \
        .replace('{$dir_fmriprep_work$}', dir_fmriprep_work) \
        .replace('{$dir_xcpd$}', dir_xcpd) \
        .replace('{$dir_xcpd_cifti$}', dir_xcpd_cifti) \
        .replace('{$dir_xcpd_work$}', dir_xcpd_work)

    file_bash = open(file_bash, 'w')
    print(template_content, file=file_bash)
    file_bash.close()

    # output workflow.sh
    file_bash = os.path.join(dir_script_cluster, sub_ses, 'workflow.sh')
    file_bash = open(file_bash, 'w')
    print(workflow_content, file=file_bash)
    file_bash.close()

print(f"All scripts are generated successfully\n")
# ============================================== #

# # ============= start run workflow ============ #
# file_bash = os.path.join(dir_script, 'workflow', 'workflow_cluster.sh')
# logFile = os.path.join(dir_abcd_result, 'Log', 'Log_workflow_cluster.log')
# n_thread = 1
# memory = '5G'
# maxProgress = 200  # 200 max workflows
# minSpace = 1000  # 1000GB free space at least to submit new jobs

# file_bash = os.path.join(dir_script_cluster, 'workflow_cluster.sh')
# logFile = os.path.join(dir_script_cluster, 'Log_workflow_cluster.log')
# if os.path.exists(logFile):
#     subprocess.run(['rm','-rf',logFile])
# # file_resubmit_info = os.path.join(dir_script_cluster, 'List_resubmit.txt')
# file_resubmit_info = ''
# dir_main = dir_abcd_result

# with open(file_template_workflow_cluster, 'r') as file:
#     template_content = file.read()
#     template_content = template_content \
#         .replace('{$date_time$}', str(date_time)) \
#         .replace('{$job_submit_command$}',
#                  f'{submit_command} {thread_command}{n_thread} {memory_command}{memory} {log_command}{logFile} {file_bash}') \
#         .replace('{$subject$}', subjectID) \
#         .replace('{$session$}', sessionID) \
#         .replace('{$dir_main$}', dir_main) \
#         .replace('{$flag_continue$}', str(flag_continue)) \
#         .replace('{$maxProgress$}', str(maxProgress)) \
#         .replace('{$minSpace$}', str(minSpace)) \
#         .replace('{$dir_script_cluster$}', dir_script_cluster) \
#         .replace('{$file_resubmit_info$}', file_resubmit_info)

# file_bash = os.path.join(dir_script_cluster, 'workflow_cluster.sh')
# file_bash = open(file_bash, 'w')
# print(template_content, file=file_bash)
# file_bash.close()

# # submit_command = ['qsub', '-terse', '-j', 'y', '-pe', 'threaded', str(n_thread), '-l', 'h_vmem='+memory, '-o', logFile, file_bash.name]
# # subprocess.run(submit_command)

# print(f"workflow job is submitted\n")
# # ============================================== #
