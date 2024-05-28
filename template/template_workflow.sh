#!/bin/sh
#{$job_setting$}

# This bash script is to run the abcd_fmri_preprocess workflow for one subject
# The script is generated based on the toolbox abcd_fmri_preprocess (/template/template_workflow.sh)
# created on {$date_time$}

# Use command to run this job:
# $ {$job_submit_command$}

subject={$subject$}
session={$session$}

dir_script_sub={$dir_script_sub$}
dir_bids_temp_sub={$dir_bids_temp_sub$}
dir_fmriprep_temp_sub={$dir_fmriprep_temp_sub$}
dir_xcpd_temp_sub={$dir_xcpd_temp_sub$}

# run raw2bids.sh
bash $dir_script_sub'/raw2bids.sh'

rm -rf ${dir_bids_temp_sub}

# run fmriprep.sh
bash $dir_script_sub'/fmriprep.sh'

rm -rf ${dir_fmriprep_temp_sub}

# run xcpd.sh
bash $dir_script_sub'/xcpd.sh'

rm -rf ${dir_fmriprep_xcpd_sub}

