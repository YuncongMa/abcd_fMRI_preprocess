# Yuncong Ma, 2/23/2024
# Copy some data from ABCD
# source activate /cbica/home/mayun/.conda/envs/pnet
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
list_subject = np.array(('NDARINV003RTV85', 'NDARINV005V6D2C','NDARINVPZUFXXY1', 'NDARINV84PUG220','NDARINV8BMH9VM4'))
n_subject = len(list_subject)

# must contain baseline
keyword = 'baseline'

# keywords
list_keyword = np.array(('rsfMRI', 'fMRI-FM', 'T1', 'T2'))

# find files
for root, dirs, files in os.walk(dir_raw_data):
    # ex. file name:  NDARINV0A4P0LWM_2YearFollowUpYArm1_ABCD-rsfMRI_20200229132104.tgz
    for filename in files:
        if filename.endswith('.tgz') and keyword in filename:
            info_subjectID = filename[0:filename.find('_')]
            if not info_subjectID in list_subject:
                continue
            
            flag = 0
            for i in range(len(list_keyword)):
                if list_keyword[i] in filename:
                    flag = 1
                    break
            if flag == 1:
                shutil.copyfile(os.path.join(dir_raw_data, filename),os.path.join(dir_output, filename))

