# Yuncong Ma, 2/21/2024
# Unpack tgz files and convert them into NII format
# Rename files
# This code is adapted from abcd-dicom2bids/src/unpack_and_setup.sh
# All four pairs of field maps will be kept for future selection
# This code does NOT work for DTI/DWI data

# packages
import os
import re
import sys
import subprocess
import numpy as np
import bids

# ========== directories
# directories of data
dir_abcd_test = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
dir_raw_data = os.path.join(dir_abcd_test, 'Example_Data')
dir_temp = os.path.join(dir_abcd_test, 'Temp')
dir_dcm = os.path.join(dir_abcd_test, 'DCM')
dir_bids = os.path.join(dir_abcd_test, 'BIDS')

# directory of this package
dir_abcd_fmri_preprocess = os.path.dirname(os.path.realpath(__file__))
dir_abcd2bids = os.path.join(dir_abcd_fmri_preprocess, 'abcd-dicom2bids-master')

# directory of FSL 5.0.1
dir_fsl = '/usr/local/fsl'


# clean out and create the DCM folder
# if not os.path.exists(dir_dcm):
#     os.makedirs(dir_dcm)
# clean out and create the BIDS folder
if not os.path.exists(dir_bids):
    os.makedirs(dir_bids)
if not os.path.exists(dir_temp):
    os.makedirs(dir_temp)

# copy BIDS description file
shutil.copyfile(os.path.join(dir_abcd_yuncong, 'dataset_description.json'), os.path.join(dir_bids, 'dataset_description.json'))

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

# for _, sub in enumerate(subject_unique):
#     indexes = [index for index, value in enumerate(list_sub) if value == sub]
#     SESSION = list_session[indexes[0]]
#     print(sub+'  '+SESSION)
#
#     # unpack tgz files
#     for i in indexes:
#         subprocess.run(['tar', '-xzf', list_file[i], '-C', dir_dcm])
#
#     # remove some volumes for functional data
#     if os.path.exists(os.path.join(dir_dcm, sub, SESSION, 'func')):
#         subprocess.run([os.path.join(dir_abcd2bids, 'src/remove_RawDataStorage_dcms.py'), os.path.join(dir_dcm, sub, SESSION, 'func')])
#
#     # convert DCM to BIDS and move to ABCD directory
#     participant = sub[4:]
#     session = SESSION[4:]
#     print(participant+' - '+session)
#     os.makedirs(os.path.join(dir_dcm, sub, 'BIDS_unprocessed'))
#     subprocess.run(['cp', os.path.join(dir_abcd2bids, 'data', 'dataset_description.json'), os.path.join(dir_dcm, sub, 'BIDS_unprocessed')])
#     subprocess.run(['dcm2bids', '-d', os.path.join(dir_dcm, sub), '-p', participant, '-s', session, '-c', os.path.join(dir_abcd2bids, 'abcd_dcm2bids.conf'),
#                     '-o', os.path.join(dir_dcm, sub, 'BIDS_unprocessed'), '--force_dcm2bids', '--clobber'])
#
#     print('\n\n')


def keyword_in_string(keywords, text):
    for keyword in keywords:
        if keyword in text:
            return True
    return False


# process for each subject and each session
for _, subject in enumerate(subject_unique):
    indexes = [index for index, value in enumerate(list_sub) if value == subject]
    SESSION = list_session[indexes[0]]

    # Unpack/setup the data for this subject/session
    dir_temp_sub = os.path.join(dir_temp, subject+'_'+SESSION)
    if not os.path.exists(dir_temp_sub):
        os.makedirs(dir_temp_sub)
    # only copy anat and rsfMRI data
    Keywords = ['ABCD-T1', 'ABCD-T2', 'ABCD-fMRI', 'ABCD-rsfMRI']
    # generate a scan file
    list_sub_scan = os.path.join(dir_temp_sub, 'List_Scan.txt')
    list_sub_scan = open(list_sub_scan, 'w')
    for _, i in enumerate(indexes):
        if keyword_in_string(Keywords, list_file[i]):
            print(list_file[i], file=list_sub_scan)
    list_sub_scan.close()
    list_sub_scan = list_sub_scan.name
    subprocess.run(['bash', os.path.join(dir_abcd_fmri_preprocess, 'unpack_and_setup_yuncong.sh'),
                    subject,
                    SESSION,
                    dir_raw_data,
                    dir_abcd2bids,
                    dir_bids,
                    dir_temp_sub,
                    dir_abcd_fmri_preprocess,
                    list_sub_scan
                    ])

    # # select the best field map
    # subprocess.run(['bash', os.path.join(dir_abcd_fmri_preprocess, 'select_fmap.sh'),
    #                 subject,
    #                 SESSION,
    #                 dir_raw_data,
    #                 dir_abcd2bids,
    #                 dir_bids,
    #                 dir_temp,
    #                 dir_fsl,
    #                 dir_abcd_yuncong
    #                 ])

# check bids
# BIDS = bids.BIDSLayout(dir_bids, is_derivative=True)
# print(BIDS.get(subject='NDARINV003RTV85', session='baselineYear1Arm1', datatype='fmap', suffix='AP', extension='.nii.gz'))



