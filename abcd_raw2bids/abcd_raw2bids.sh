# Yuncong Ma, 2/26/2024
# Try the dcm2bids_yuncong.py
# dir_main=/cbica/home/mayun/Projects/ABCD
# qsub -terse -j y -pe threaded 4 -l h_vmem=10G -o ${dir_main}/Log/abcd_raw2bids.log ${dir_main}/Script/abcd_raw2bids/abcd_raw2bids.sh

# specify packages
# module load dcm2bids
# module load dcm2niix
# module load dcmtk

source activate /cbica/home/mayun/.conda/envs/abcd
dir_python=~/.conda/envs/abcd/bin/python

dir_main=/cbica/home/mayun/Projects/ABCD

${dir_python} ${dir_main}/Script/abcd_raw2bids/abcd_raw2bids.py
