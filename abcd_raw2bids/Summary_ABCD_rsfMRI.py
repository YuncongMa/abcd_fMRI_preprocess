# Yuncong Ma, 1/24/2024
# Extract scan infomartion of ABCD
# source activate /cbica/home/mayun/.conda/envs/pnet
# python /cbica/home/mayun/Projects/ABCD/Script/Preprocessing/Summary_ABCD_rsfMRI.py

import os
import re
import nibabel as nib
import numpy as np
import sys

#dir_pnet = '/cbica/home/mayun/Projects/NiChart/pNet'
#sys.path.append(os.path.join(dir_pnet, 'Python'))
#import pNet

# get fMRI scan information
dir_raw_data = '/cbica/projects/ABCD_Data_Releases/Data/image03'
dir_scan_info = '/cbica/home/mayun/Projects/ABCD/Scan_Info'

# basic info
list_scan = []
list_subject_ID = []
list_year = []

# summary
stat_subject = 0
stat_year = np.zeros(6)
stat_followup = []

for root, dirs, files in os.walk(dir_raw_data):
    # ex. file name:  NDARINV0A4P0LWM_2YearFollowUpYArm1_ABCD-rsfMRI_20200229132104.tgz
    for filename in files:
        if filename.endswith('.tgz') and 'rsfMRI' in filename and 'fMRI-FM' not in filename:
            list_scan.append(os.path.join(root, filename))
            
            info_subjectID = filename[0:filename.find('_')]
            list_subject_ID.append(info_subjectID)
            
            if 'baseline' in filename:
                info_year = '1'
            else:  
                info_year = re.search(r'(\d)YearFollowUp', filename)[0][0]
                
            list_year.append(info_year)

# sort list by the user ID
index_sort = np.argsort(list_subject_ID)
#print(index_sort)
list_subject_ID = np.array(list_subject_ID)[index_sort]
list_year = np.array(list_year)[index_sort]
list_scan = np.array(list_scan)[index_sort]

print(len(list_scan))
# output
file_scan_list = os.path.join(dir_scan_info, 'Scan_List.txt')
file_scan_list = open(file_scan_list, 'w')
for i in range(len(list_scan)):
    print(list_scan[i], file=file_scan_list)
file_scan_list.close()

file_subject_ID = os.path.join(dir_scan_info, 'Subject_ID.txt')
file_subject_ID = open(file_subject_ID, 'w')
for i in range(len(list_subject_ID)):
    print(list_subject_ID[i], file=file_subject_ID)
file_subject_ID.close()

file_list_year = os.path.join(dir_scan_info, 'Year_List.txt')
file_list_year = open(file_list_year, 'w')
for i in range(len(list_year)):
    print(list_year[i], file=file_list_year)
file_list_year.close()

# summary
stat_subject = list(dict.fromkeys(list_subject_ID))
n_subject = len(stat_subject)
print('Number of subjects = '+str(n_subject))
file_subject_ID_unique = os.path.join(dir_scan_info, 'Subject_ID_Unique.txt')
file_subject_ID_unique = open(file_subject_ID_unique, 'w')
for i in range(n_subject):
    print(stat_subject[i], file=file_subject_ID_unique)
file_subject_ID_unique.close()

for i in range(len(list_subject_ID)):
    stat_year[int(list_year[i])] = stat_year[int(list_year[i])]+1

print('Scans per year:')
for i in range(1, len(stat_year)):
    print('  Year '+str(i)+' = '+str(stat_year[i]))

stat_subject_year = np.zeros(6)
for i in range(0, 6):
    if str(i) in list_year:
        indices = [int(ind) for ind, ele in enumerate(list_year) if ele == str(i)]
        stat_subject_year[i] = len(list(dict.fromkeys(np.array(list_subject_ID)[indices])))
    
print('Subjects per year:')
for i in range(1, len(stat_subject_year)):
    print('  Year '+str(i)+' = '+str(stat_subject_year[i]))
    
stat_subject_year = np.zeros((n_subject, 6))
for i in range(0, 6):
    if str(i) in list_year:
        indices = [int(ind) for ind, ele in enumerate(list_year) if ele == str(i)]
        temp = list(dict.fromkeys(np.array(list_subject_ID)[indices]))
        for j in range(n_subject):
            if stat_subject[j] in temp:
                stat_subject_year[j, i] = 1

print(np.unique(np.sum(stat_subject_year, axis=1), return_counts=True))