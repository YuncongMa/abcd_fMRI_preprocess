#!/bin/bash
# Yuncong Ma, 4/9/2024
# zip BIDS_QC results by subject-session for easier download
# bash /cbica/home/mayun/Projects/ABCD/Script/workflow/zip_BIDS_QC.sh
# submit job
# dir_main=/cbica/home/mayun/Projects/ABCD
# qsub -terse -j y -pe threaded 8 -l h_vmem=5G -o $dir_main/Log/Log_zip_BIDS_QC.log $dir_main/Script/workflow/zip_BIDS_QC.sh

echo -e "\nStart zip_BIDS_QC.sh: `date +%F-%H:%M:%S`\n"

# skip previously zipped BIDS_QC results
flag_continue=1

# directories for storing zipped BIDS_QC results
dir_bids_qc=/cbica/home/mayun/Projects/ABCD/BIDS_QC
dir_bids_qc_zip=/cbica/home/mayun/Projects/ABCD/BIDS_QC_zip

# create folder
if [[ ! -d "$dir_bids_qc_zip" ]]; then
    mkdir -p $dir_bids_qc_zip
fi

# find html reports
list_html=($(find $dir_bids_qc -maxdepth 1 -type f -name *.html))
let n_html=${#list_html[@]}

echo -e "find $n_html reports"

cd $dir_bids_qc

for ((i = 0; i <$n_html; i++)); do
    file_name=`echo "${list_html[$i]}" | cut -d'.' -f1`
    file_name=`basename ${file_name}`

    file_zip=$dir_bids_qc_zip/$file_name.zip
    if [ "$flag_continue" -eq "0" ]; then
        if test -f "$file_zip"; then
            rm -rf "$file_zip"
        fi
        echo -e "zip to $file_zip"
        zip -q -T -m -r $file_zip $file_name $file_name.html $file_name.txt
    else
        if test -f "$file_zip"; then
            continue
        else
            echo -e "zip to $file_zip"
            zip -q -T -m -r $file_zip $file_name $file_name.html $file_name.txt
        fi
    fi
done

echo -e "\nFinished zip_BIDS_QC.sh: `date +%F-%H:%M:%S`\n"

