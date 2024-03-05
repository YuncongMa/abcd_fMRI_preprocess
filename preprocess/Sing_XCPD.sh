# Yuncong Ma, 3/4/2024
# build XCP-D in singularity
# dir_main=/cbica/home/mayun/Projects/ABCD
# qsub -terse -j y -pe threaded 4 -l h_vmem=32G -o ${dir_main}/Log/Sing_XCPD.log ${dir_main}/Script/preprocess/Sing_XCPD.sh

singularity build /cbica/home/mayun/Toolbox/xcp_d-0.6.2.simg docker://pennlinc/xcp_d:0.6.2