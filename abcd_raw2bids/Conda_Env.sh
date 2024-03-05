# Yuncong Ma, 2/28/2024
# Prepare a Python environment in Conda for preprocessing ABCD dataset
# dir_main=/cbica/home/mayun/Projects/ABCD
# qsub -terse -j y -pe threaded 1 -l h_vmem=10G -o ${dir_main}/Log/Conda_Env.log ${dir_main}/Script/Preprocessing/Conda_Env.sh

echo -e "\nRunning Conda_Env.sh on                       : `hostname`"
echo -e "Start time                                   : `date +%F-%H:%M:%S`\n"

conda create -n abcd python=3.8

source activate /cbica/home/mayun/.conda/envs/abcd 

cd /cbica/home/mayun/Projects/ABCD/Package/abcd-dicom2bids-master
