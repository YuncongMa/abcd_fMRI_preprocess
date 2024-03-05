# Yuncong Ma, 3/5/2024
# ABCD raw data to preprocessed data in a cluster environment
# This code does NOT work for DTI data

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
dir_env = '/cbica/home/mayun/.conda/envs/abcd'

# Test mode on local computer
cluster = 0

# setup the directory of the pNet toolbox folder
if cluster:
    dir_script = '/cbica/home/mayun/Projects/ABCD/Script'
    dir_python = '~/.conda/envs/abcd/bin/python'
    sys.path.append(dir_script)
    dir_abcd_test = os.path.dirname(dir_script)
    dir_fsl = '/cbica/software/external/fsl/centos7/5.0.11'
else:
    dir_script = os.path.dirname(os.path.abspath(__name__))
    dir_abcd_test = os.path.dirname(dir_script)
    dir_fsl = '/usr/local/fsl'

# directories of sub-scripts
dir_abcd_raw2bids = os.path.join(dir_script, 'abcd_raw2bids')
dir_abcd2bids = os.path.join(dir_script, 'abcd_raw2bids', 'abcd-dicom2bids-master')

# directories of raw data and folders for different steps in preprocessing
# raw data
dir_raw_data = os.path.join(dir_abcd_test, 'Example_Data')
# temporary folders for BIDS
dir_bids = os.path.join(dir_abcd_test, 'BIDS')
dir_bids_temp = os.path.join(dir_abcd_test, 'BIDS_Temp')
dir_fmriprep = os.path.join(dir_abcd_test, 'fmriprep')
dir_fmriprep_work = os.path.join(dir_abcd_test, 'fmriprep_work')
dir_xcpd = os.path.join(dir_abcd_test, 'XCP_D')
dir_xcpd_work = os.path.join(dir_abcd_test, 'XCP_D_work')

# directory to save scripts for cluster
dir_script_cluster = os.path.join(dir_abcd_test, 'Script_Cluster')

# singularity images for fmriprep and xcp-d
file_fmriprep = os.path.join(dir_abcd_test, 'Tool', 'nipreps_fmriprep_23.0.2.simg')
file_xcpd = os.path.join(dir_abcd_test, 'Tool', 'xcp_d-0.6.2.simg')

# setting for fmriprep
file_fs_license = ''
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
# ============================================== #

# ======= start to extract raw data info ======= #
print(f"Start to extract scan info from raw data folder {dir_raw_data}")
# create folders
if not os.path.exists(dir_bids):
    os.makedirs(dir_bids)
if not os.path.exists(dir_bids_temp):
    os.makedirs(dir_bids_temp)
if not os.path.exists(dir_script_cluster):
    os.makedirs(dir_script_cluster)

# copy BIDS description file
shutil.copyfile(os.path.join(dir_abcd_raw2bids, 'dataset_description.json'), os.path.join(dir_bids, 'dataset_description.json'))

# extract information of tgz files, subject and session
list_file = []
list_sub = []
list_session = []
for root, dirs, files in os.walk(dir_raw_data):
    for filename in files:
        if filename.endswith(".tgz") and filename.__contains__("baselineYear1Arm1"):
            Keywords = filename.split('_')
            SUB = 'sub-'+Keywords[0]
            session = 'ses-'+Keywords[1]
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
    # only test on selected subjects
    # if subject not in ['sub-NDARINVPZUFXXY1']:
    #     continue

    # get session info
    indexes = [index for index, value in enumerate(list_sub) if value == subject]
    session = list_session[indexes[0]]

    # make subject-session directory for cluster script
    if not os.path.exists(os.path.join(dir_script_cluster, subject+'_'+session)):
        os.makedirs(os.path.join(dir_script_cluster, subject+'_'+session))

    dir_temp_sub = os.path.join(dir_bids_temp, subject+'_'+session)

    # Unpack/setup the data for this subject/session
    # only copy anat and rsfMRI data
    Keywords = ['ABCD-T1', 'ABCD-T2', 'FM', 'ABCD-rsfMRI']
    # generate a scan file
    list_sub_scan = os.path.join(dir_script_cluster, subject+'_'+session, 'List_Scan.txt')
    list_sub_scan = open(list_sub_scan, 'w')
    for _, i in enumerate(indexes):
        if keyword_in_string(Keywords, list_file[i]):
            print(list_file[i], file=list_sub_scan)
    list_sub_scan.close()

    # convert raw data to bids format
    n_thread = 4
    memory = '10G'
    file_bash = os.path.join(dir_script_cluster, subject+'_'+session, 'submit_unpack.sh')
    file_bash = open(file_bash, 'w')
    logFile = os.path.join(dir_script_cluster, subject+'_'+session, 'Log_unpack.log')

    # ====== step 1: raw data to BIDS
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    file_bash_unpack = os.path.join(dir_abcd_raw2bids, 'unpack_and_setup_yuncong.sh')
    print('#!/bin/sh\n', file=file_bash)
    print('# This bash script is to run unpack_and_setup_yuncong.sh', file=file_bash)
    print(f'# created on {date_time}\n', file=file_bash)
    print(f'# Use command to submit this job:\n# $ {submit_command} {thread_command}{n_thread} {memory_command}{memory} {log_command}{logFile} {file_bash.name}\n', file=file_bash)
    print(r'echo -e "Start time : `date +%F-%H:%M:%S`\n" ', file=file_bash)
    print(f'\nsource activate  {dir_env}\n', file=file_bash)
    print(r'# settings\n', file=file_bash)
    print(f'file_bash_unpack={file_bash_unpack}', file=file_bash)
    print(f'subject={subject}', file=file_bash)
    print(f'session={session}', file=file_bash)
    print(f'dir_raw_data={dir_raw_data}', file=file_bash)
    print(f'dir_abcd2bids={dir_abcd2bids}', file=file_bash)
    print(f'dir_bids={dir_bids}', file=file_bash)
    print(f'dir_temp_sub={dir_temp_sub}', file=file_bash)
    print(f'dir_abcd_raw2bids={dir_abcd_raw2bids}', file=file_bash)
    print(f'list_sub_scan={list_sub_scan.name}', file=file_bash)
    print(f'\nbash $file_bash_unpack $subject $session $dir_raw_data $dir_abcd2bids $dir_bids $dir_temp_sub $dir_abcd_raw2bids $list_sub_scan\n', file=file_bash)
    print(r'echo -e "Finished time : `date +%F-%H:%M:%S`\n" ', file=file_bash)
    file_bash.close()

    # ====== step 2: QC for BIDS
    # generate qc for bids results
    # check whether PhaseEncodingDirection in fMRI map is correct, by comparing to the field map with the same direction
    n_thread = 4
    memory = '10G'
    file_bash = os.path.join(dir_script_cluster, subject+'_'+session, 'submit_qc_bids.sh')
    file_bash = open(file_bash, 'w')
    logFile = os.path.join(dir_script_cluster, subject+'_'+session, 'Log_qc.log')

    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    file_qc = os.path.join(dir_abcd_raw2bids, 'qc_bids.py')
    print('#!/bin/sh\n', file=file_bash)
    print('# This bash script is to run submit_qc_bids.sh', file=file_bash)
    print(f'# created on {date_time}\n', file=file_bash)
    print(f'# Use command to submit this job:\n# $ {submit_command} {thread_command}{n_thread} {memory_command}{memory} {log_command}{logFile} {file_bash.name}\n', file=file_bash)
    print(r'echo -e "Start time : `date +%F-%H:%M:%S`\n" ', file=file_bash)
    print(f'\nsource activate  {dir_env}\n', file=file_bash)
    print(r'# settings\n', file=file_bash)
    print(f'file_qc={file_qc}', file=file_bash)
    print(f'subject={subject}', file=file_bash)
    print(f'session={session}', file=file_bash)
    print(f'dir_bids={dir_bids}', file=file_bash)
    print(f'dir_abcd_raw2bids={dir_abcd_raw2bids}', file=file_bash)
    print(f'\npython $file_qc $subject $session $dir_bids $dir_fsl dir_abcd_raw2bids\n', file=file_bash)
    print(r'echo -e "Finished time : `date +%F-%H:%M:%S`\n" ', file=file_bash)
    file_bash.close()

    # ====== step 3: fmriprep
    n_thread = 4
    memory = '64G'
    file_bash = os.path.join(dir_script_cluster, subject+'_'+session, 'submit_fmriprep.sh')
    file_bash = open(file_bash, 'w')
    logFile = os.path.join(dir_temp_sub, 'Log_fmriprep.log')
    print('#!/bin/sh\n', file=file_bash)
    print('# This bash script is to run fmriprep', file=file_bash)
    print(f'# created on {date_time}\n', file=file_bash)
    print(f'# Use command to submit this job:\n# $ {submit_command} {thread_command}{n_thread} {memory_command}{memory} {log_command}{logFile} {file_bash.name}\n', file=file_bash)
    print(r'echo -e "Start time : `date +%F-%H:%M:%S`\n" ', file=file_bash)
    print('\nunset PYTHONPATH\n', file=file_bash)
    print(f'file_fmriprep={file_fmriprep}', file=file_bash)
    print(f'dir_bids={dir_bids}', file=file_bash)
    print(f'dir_output={dir_fmriprep}', file=file_bash)
    print(f'n_thread={n_thread}', file=file_bash)
    print(f'max_mem={memory}', file=file_bash)
    print(f'file_fs_license={file_fs_license}', file=file_bash)
    print(f'n_dummy={n_dummy}', file=file_bash)
    print(f'dir_fmriprep_work={dir_fmriprep_work}', file=file_bash)
    print(f'sub_id={subject[4:]}', file=file_bash)
    print(f'output_space={fmriprep_output_space}', file=file_bash)
    print(f'\nsingularity run --cleanenv $file_fmriprep '
          f'$dir_bids $dir_output '
          f'--nthreads $n_thread --mem_mb $max_mem '
          f'--fs-license-file $file_fs '
          f'--dummy-scans $n_dummy '
          f'--cifti-output "32k" '
          f'-w $dir_fmriprep_work '
          f'--participant-label $sub_id '
          f'--output-space --use-aroma',
          file=file_bash)
    print(f'\n'r'echo -e "Finished time : `date +%F-%H:%M:%S`\n" ', file=file_bash)
    file_bash.close()

    # ====== step 4: XCP-D
    n_thread = 4
    memory = '11G'
    memory_xcpd = 10
    file_bash = os.path.join(dir_script_cluster, subject+'_'+session, 'submit_xcpd.sh')
    file_bash = open(file_bash, 'w')
    logFile = os.path.join(dir_script_cluster, subject+'_'+session, 'Log_xcpd.log')
    print('#!/bin/sh\n', file=file_bash)
    print('# This bash script is to run fmriprep', file=file_bash)
    print(f'# created on {date_time}\n', file=file_bash)
    print(
        f'# Use command to submit this job:\n# $ {submit_command} {thread_command}{n_thread} {memory_command}{memory} {log_command}{logFile} {file_bash.name}\n',
        file=file_bash)
    print(f'file_xcpd={file_xcpd}', file=file_bash)
    print(f'dir_bids={dir_bids}', file=file_bash)
    print(f'dir_output={dir_fmriprep}', file=file_bash)
    print(f'n_thread={n_thread}', file=file_bash)
    print(f'max_mem={memory}', file=file_bash)
    print(f'file_fs_license={file_fs_license}', file=file_bash)
    print(f'sub_id={subject[4:]}', file=file_bash)
    print(f'n_dummy={n_dummy}', file=file_bash)
    print(f'dir_output={dir_xcpd}', file=file_bash)
    print(f'fwhm={fwhm}', file=file_bash)
    print(f'confound={confound}', file=file_bash)
    print(f'bp_low={bp_low}', file=file_bash)
    print(f'bp_high={bp_high}', file=file_bash)
    print(f'bp_order={bp_order}', file=file_bash)
    print(f'fd_threshold={fd_threshold}', file=file_bash)
    print(f'dir_xcpd_work={dir_xcpd_work}', file=file_bash)
    print(f'fd_threshold={fd_threshold}', file=file_bash)
    print(f'$file_log_job={logFile}', file=file_bash)
    print(f'\n'r'echo -e "Start time : `date +%F-%H:%M:%S`\n" ', file=file_bash)
    print(f'\nsingularity run --cleanenv $file_xcpd '
          f'--nthreads $n_thread --memory $max_mem '
          f'-log $file_log_job '
          f'--fs-license-file $file_fs '
          f'--n_dummy $n_dummy '
          f'-fmriprep $dir_fmriprep'
          f'-output $dir_output '
          f'-fwhm $fwhm '
          f'-confound $confound '
          f'-bp_low $bp_low '
          f'bp_high $bp_high '
          f'-bp_order $bp_order '
          f'-fd_threshold $fd_threshold'
          f'--work_dir $dir_xcpd_work'
          f'--participant-label $sub_id',
          file=file_bash)
    print(f'\n'r'echo -e "Finished time : `date +%F-%H:%M:%S`\n" ', file=file_bash)
    file_bash.close()

print(f"All scripts are generated successfully\n")
# ============================================== #

# ============= start run bash jobs ============ #


# ============================================== #
