# Yuncong Ma, 3/4/2024
# ABCD raw data to BIDS format in a cluster environment
# Unpack tgz files and convert them into NII format
# Rename files
# Prepare BIDS formatted data
# Select the best field maps, labeled in their JSON files
# This code is adapted from abcd-dicom2bids/src/unpack_and_setup.sh
# All four pairs of field maps will be kept for future selection
# This code does NOT work for DTI data

# packages
import glob
import os
import shutil
import subprocess
from datetime import datetime
import numpy as np

# setting for the cluster environment and conda
submit_command = 'qsub -terse -j y'
thread_command = '-pe threaded '
memory_command = '-l h_vmem='
log_command = '-o '
dir_env = '/cbica/home/mayun/.conda/envs/abcd'

# directories
dir_abcd_test = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
dir_abcd_fmri_preprocess = os.path.join(dir_abcd_test, 'Python')
dir_abcd2bids = os.path.join(dir_abcd_test, 'Python', 'abcd-dicom2bids-master')
dir_raw_data = os.path.join(dir_abcd_test, 'Example_Data')
# script
dir_script_cluster = os.path.join(dir_abcd_test, 'Script_Cluster')
# raw2bids
dir_temp = os.path.join(dir_abcd_test, 'Temp')
dir_dcm = os.path.join(dir_abcd_test, 'DCM')
dir_bids = os.path.join(dir_abcd_test, 'BIDS')
dir_fsl = '/usr/local/fsl'
# fmriprep
dir_fmriprep = os.path.join(dir_abcd_test, 'fmriprep')
dir_fmriprep_work = os.path.join(dir_abcd_test, 'fmriprep_work')
file_fmriprep = os.path.join(dir_abcd_test, 'Tool', 'nipreps_fmriprep_23.0.2.simg')
file_fs_license = ''
n_dummy = 10
fmriprep_output_space = 'MNI152NLin6Asym:res-2'
# xcpd
file_xcpd = os.path.join(dir_abcd_test, 'Tool', 'xcp_d-0.6.2.simg')

# create folders
if not os.path.exists(dir_bids):
    os.makedirs(dir_bids)
if not os.path.exists(dir_temp):
    os.makedirs(dir_temp)
if not os.path.exists(dir_script_cluster):
    os.makedirs(dir_script_cluster)

# copy BIDS description file
shutil.copyfile(os.path.join(dir_abcd_fmri_preprocess, 'dataset_description.json'), os.path.join(dir_bids, 'dataset_description.json'))

# extract information of tgz files, subject and session
list_file = []
list_sub = []
list_session = []
for root, dirs, files in os.walk(dir_raw_data):
    for filename in files:
        if filename.endswith(".tgz") and filename.__contains__("baselineYear1Arm1"):
            #print(filename)
            Keywords = filename.split('_')
            SUB = 'sub-'+Keywords[0]
            SESSION = 'ses-'+Keywords[1]
            list_file.append(os.path.join(root, filename))
            list_sub.append(SUB)
            list_session.append(SESSION)

subject_unique = np.unique(np.array(list_sub))


def keyword_in_string(keywords, text):
    for keyword in keywords:
        if keyword in text:
            return True
    return False


# process for each subject and each session
# prepare files
for _, subject in enumerate(subject_unique):

    indexes = [index for index, value in enumerate(list_sub) if value == subject]
    SESSION = list_session[indexes[0]]

    # Unpack/setup the data for this subject/session
    dir_temp_sub = os.path.join(dir_temp, subject+'_'+SESSION)
    if not os.path.exists(dir_temp_sub):
        os.makedirs(dir_temp_sub)
    # only copy anat and rsfMRI data
    Keywords = ['ABCD-T1', 'ABCD-T2', 'FM', 'ABCD-rsfMRI']
    # generate a scan file
    list_sub_scan = os.path.join(dir_temp_sub, 'List_Scan.txt')
    list_sub_scan = open(list_sub_scan, 'w')
    for _, i in enumerate(indexes):
        if keyword_in_string(Keywords, list_file[i]):
            print(list_file[i], file=list_sub_scan)
    list_sub_scan.close()

# Generate bash scripts
for _, subject in enumerate(subject_unique):
    # only test on selected subjects
    # if subject not in ['sub-NDARINVPZUFXXY1']:
    #     continue

    if not os.path.exists(os.path.join(dir_script_cluster, subject+'_'+SESSION)):
        os.makedirs(os.path.join(dir_script_cluster, subject+'_'+SESSION))

    dir_temp_sub = os.path.join(dir_temp, subject+'_'+SESSION)
    indexes = [index for index, value in enumerate(list_sub) if value == subject]
    SESSION = list_session[indexes[0]]

    indexes = [index for index, value in enumerate(list_sub) if value == subject]
    SESSION = list_session[indexes[0]]

    # Unpack/setup the data for this subject/session
    # only copy anat and rsfMRI data
    Keywords = ['ABCD-T1', 'ABCD-T2', 'FM', 'ABCD-rsfMRI']
    # generate a scan file
    list_sub_scan = os.path.join(dir_script_cluster, subject+'_'+SESSION, 'List_Scan.txt')
    list_sub_scan = open(list_sub_scan, 'w')
    for _, i in enumerate(indexes):
        if keyword_in_string(Keywords, list_file[i]):
            print(list_file[i], file=list_sub_scan)
    list_sub_scan.close()

    # convert raw data to bids format
    n_thread = 4
    memory = '10G'
    file_bash = os.path.join(dir_script_cluster, subject+'_'+SESSION, 'submit_unpack.sh')
    file_bash = open(file_bash, 'w')
    logFile = os.path.join(dir_script_cluster, subject+'_'+SESSION, 'Log_unpack.log')

    # ====== step 1: raw data to BIDS
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    file_bash_unpack = os.path.join(dir_abcd_fmri_preprocess, 'unpack_and_setup_yuncong.sh')
    print('#!/bin/sh\n', file=file_bash)
    print('# This bash script is to run unpack_and_setup_yuncong.sh', file=file_bash)
    print(f'# created on {date_time}\n', file=file_bash)
    print(f'# Use command to submit this job:\n# $ {submit_command} {thread_command}{n_thread} {memory_command}{memory} {log_command}{logFile} {file_bash.name}\n', file=file_bash)
    print(r'echo -e "Start time : `date +%F-%H:%M:%S`\n" ', file=file_bash)
    print(f'\nsource activate  {dir_env}\n', file=file_bash)
    print(r'# settings\n', file=file_bash)
    print(f'file_bash_unpack={file_bash_unpack}', file=file_bash)
    print(f'subject={subject}', file=file_bash)
    print(f'SESSION={SESSION}', file=file_bash)
    print(f'dir_raw_data={dir_raw_data}', file=file_bash)
    print(f'dir_abcd2bids={dir_abcd2bids}', file=file_bash)
    print(f'dir_bids={dir_bids}', file=file_bash)
    print(f'dir_temp_sub={dir_temp_sub}', file=file_bash)
    print(f'dir_abcd_fmri_preprocess={dir_abcd_fmri_preprocess}', file=file_bash)
    print(f'list_sub_scan={list_sub_scan.name}', file=file_bash)
    print(f'\nbash $file_bash_unpack $subject $SESSION $dir_raw_data $dir_abcd2bids $dir_bids $dir_temp_sub $dir_abcd_fmri_preprocess $list_sub_scan\n', file=file_bash)
    print(r'echo -e "Finished time : `date +%F-%H:%M:%S`\n" ', file=file_bash)
    file_bash.close()

    # ====== step 2: QC for BIDS
    # generate qc for bids results
    # check whether PhaseEncodingDirection in fMRI map is correct, by comparing to the field map with the same direction
    n_thread = 4
    memory = '10G'
    file_bash = os.path.join(dir_script_cluster, subject+'_'+SESSION, 'submit_qc_bids.sh')
    file_bash = open(file_bash, 'w')
    logFile = os.path.join(dir_script_cluster, subject+'_'+SESSION, 'Log_qc.log')

    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    file_qc = os.path.join(dir_abcd_fmri_preprocess, 'qc_bids.py')
    print('#!/bin/sh\n', file=file_bash)
    print('# This bash script is to run submit_qc_bids.sh', file=file_bash)
    print(f'# created on {date_time}\n', file=file_bash)
    print(f'# Use command to submit this job:\n# $ {submit_command} {thread_command}{n_thread} {memory_command}{memory} {log_command}{logFile} {file_bash.name}\n', file=file_bash)
    print(r'echo -e "Start time : `date +%F-%H:%M:%S`\n" ', file=file_bash)
    print(f'\nsource activate  {dir_env}\n', file=file_bash)
    print(r'# settings\n', file=file_bash)
    print(f'file_qc={file_qc}', file=file_bash)
    print(f'subject={subject}', file=file_bash)
    print(f'SESSION={SESSION}', file=file_bash)
    print(f'dir_bids={dir_bids}', file=file_bash)
    print(f'dir_abcd_fmri_preprocess={dir_abcd_fmri_preprocess}', file=file_bash)
    print(f'\npython $file_qc $subject $SESSION $dir_bids $dir_fsl $dir_abcd_fmri_preprocess\n', file=file_bash)
    print(r'echo -e "Finished time : `date +%F-%H:%M:%S`\n" ', file=file_bash)
    file_bash.close()

    # ====== step 3: fmriprep
    n_thread = 4
    memory = '64G'
    file_bash = os.path.join(dir_script_cluster, subject+'_'+SESSION, 'submit_fmriprep.sh')
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
          f'--cifti-output "91k" '
          f'-w $dir_fmriprep_work '
          f'--participant-label $sub_id '
          f'--output-space --use-aroma',
          file=file_bash)
    print(f'\n'r'echo -e "Finished time : `date +%F-%H:%M:%S`\n" ', file=file_bash)
    file_bash.close()

    # ====== step 4: XCP-D
    n_thread = 4
    memory = '10G'
    file_bash = os.path.join(dir_script_cluster, subject+'_'+SESSION, 'submit_xcpd.sh')
    file_bash = open(file_bash, 'w')
    logFile = os.path.join(dir_script_cluster, subject+'_'+SESSION, 'Log_xcpd.log')

