# Yuncong Ma, 3/11/2024
# Copy some data from ABCD
# source activate /cbica/home/mayun/.conda/envs/abcd
# python /cbica/home/mayun/Projects/ABCD/Script/Example/Copy_Test_rsfMRI.py

import os
import re
import nibabel as nib
import numpy as np
import sys
import shutil

# get fMRI scan information
dir_raw_data = '/cbica/projects/ABCD_Data_Releases/Data/image03'
dir_output = '/cbica/home/mayun/Projects/ABCD/Example_Data'
if not os.path.exists(dir_output):
    os.makedirs(dir_output)

# subjects to use
file_subject_ID = os.path.join('/cbica/home/mayun/Projects/ABCD/Script/Example', 'Subject_ID.txt')
if os.path.exists(file_subject_ID):
    with open(file_subject_ID, 'r') as file:
        list_subject = [line.replace('\n', '') for line in file.readlines()]
n_subject = len(list_subject)
print(f'Found {n_subject} subjects')

# must contain baseline
keyword = 'baseline'

# keywords
list_keyword = np.array(('rsfMRI', 'fMRI-FM', 'T1', 'T2'))

# find files
for root, dirs, files in os.walk(dir_raw_data):
    # ex. file name:  NDARINV0A4P0LWM_2YearFollowUpYArm1_ABCD-rsfMRI_20200229132104.tgz
    for filename in files:
        if filename.endswith('.tgz') and keyword in filename:
            list_str = str.split(filename, '_')
            info_subjectID = list_str[0]
            info_session = list_str[1]
            if not info_subjectID in list_subject:
                continue

            dir_sub = os.path.join(dir_output, info_subjectID, info_subjectID+'-'+info_session)
            if not os.path.exists(dir_sub):
                os.makedirs(dir_sub)

            flag = 0
            for i in range(len(list_keyword)):
                if list_keyword[i] in filename:
                    flag = 1
                    break
            if flag == 1:
                shutil.copyfile(os.path.join(dir_raw_data, filename),os.path.join(dir_sub, filename))

