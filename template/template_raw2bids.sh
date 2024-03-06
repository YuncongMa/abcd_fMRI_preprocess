#!/bin/sh

# This bash script is to run unpack_and_setup_yuncong.sh
# The script is generated based on the toolbox abcd_fmri_preprocess (/template/template_raw2bids.sh)
# created on {$date_time$}

# Use command to submit this job:
# $ {$job_submit_command$}

echo -e "Start time : `date +%F-%H:%M:%S`\n" 

source activate {$dir_conda_env$}

# settings

file_bash_unpack={$file_bash_unpack$}

subject={$subject$}
session={$session$}
list_sub_scan={$list_sub_scan$}

dir_raw_data={$dir_raw_data}
dir_bids={$dir_bids}
dir_temp_sub={$dir_temp_sub}

dir_abcd2bids={$dir_abcd2bids$}
dir_abcd_raw2bids={$dir_abcd_raw2bids$}

# run raw2bids

bash $file_bash_unpack \
 $subject \
 $session \
 $dir_raw_data \
 $dir_abcd2bids \
 $dir_bids \
 $dir_temp_sub \
 $dir_abcd_raw2bids \
 $list_sub_scan

echo -e "Finished time : `date +%F-%H:%M:%S`\n" 
