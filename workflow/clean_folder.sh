# Yuncong Ma, 4/11/2024
# clean folders
# bash /cbica/home/mayun/Projects/ABCD/Script/clean_folder.sh
# Use the following code to run the cleanup
# qsub -terse -j y -pe threaded 1 -l h_vmem=4G -o /cbica/home/mayun/Projects/ABCD/Log/Log_clean.log /cbica/home/mayun/Projects/ABCD/Script/clean_folder.sh

dir_main=/cbica/home/mayun/Projects/ABCD

# script
# rm -rf $dir_main/Script_Cluster/*
# raw2bids
rm -rf $dir_main/BIDS/*
rm -rf $dir_main/BIDS_Temp/*
# bids_qc
rm -rf $dir_main/BIDS_QC/*
# # fmriprep
rm -rf $dir_main/fmriprep/*
rm -rf $dir_main/fmriprep_work/*
# # xcp_d
rm -rf $dir_main/XCP_D/*
rm -rf $dir_main/XCP_D_cifti/*
rm -rf $dir_main/XCP_D_work/*
# result
rm -rf $dir_main/Result/*

# remove job files core.*
find /cbica/home/mayun/Projects -maxdepth 1 -type f > /cbica/home/mayun/Projects/list_core.txt
find /cbica/home/mayun/Projects -maxdepth 1 -type f  -name core* -delete
