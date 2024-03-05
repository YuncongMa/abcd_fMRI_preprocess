# Yuncong Ma, 2/16/2024
# Try the dcm2bids_yuncong.py
# dir_main=/cbica/home/mayun/Projects/ABCD
# qsub -terse -j y -pe threaded 1 -l h_vmem=20G -o ${dir_main}/Log/DICOM_BIDS.log ${dir_main}/Script/Preprocessing/DICOM_BIDS.sh

dir_fsl=/cbica/software/external/fsl/5.0
dir_matlab=/cbica/software/external/matlab/R2017A

dir_data=/cbica/home/mayun/Projects/ABCD/Example_Data
dir_qc=/cbica/home/mayun/Projects/ABCD/Example_QC.txt
dir_sub=/cbica/home/mayun/Projects/ABCD/Example_Subject.txt

dir_output=/cbica/home/mayun/Projects/ABCD/BIDS
dir_temp=/cbica/home/mayun/Projects/ABCD/temp

cd /cbica/home/mayun/Projects/ABCD/Package/abcd-dicom2bids-master
python abcd2bids_yuncong.py $dir_fsl $dir_matlab --download $dir_data --start_at unpack_and_setup --qc $dir_qc --subject-list $dir_sub --output $dir_output 


python abcd2bids_yuncong.py unpack_and_setup $dir_fsl $dir_matlab --output $dir_output --download $dir_data --temp $dir_temp --qc $dir_qc --subject-list $dir_sub