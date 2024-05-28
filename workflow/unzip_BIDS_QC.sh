#!/bin/bash
# Yuncong Ma, 4/9/2024
# unzip BIDS_QC_zip results 
# bash /cbica/home/mayun/Projects/ABCD/Script/workflow/unzip_BIDS_QC.sh
# submit job
# dir_main=/cbica/home/mayun/Projects/ABCD
# qsub -terse -j y -pe threaded 8 -l h_vmem=5G -o $dir_main/Log/Log_unzip_BIDS_QC.log $dir_main/Script/workflow/unzip_BIDS_QC.sh

echo -e "\nStart unzip_BIDS_QC.sh: `date +%F-%H:%M:%S`\n"

# skip previously unzipped BIDS_QC_zip results
flag_continue=1

# directories for storing zipped BIDS_QC results
dir_bids_qc=/cbica/home/mayun/Projects/ABCD/BIDS_QC
dir_bids_qc_zip=/cbica/home/mayun/Projects/ABCD/BIDS_QC_zip

# create folder
if [[ ! -d "$dir_bids_qc" ]]; then
    mkdir -p $dir_bids_qc
fi

# find zipped files
list_zip=($(find $dir_bids_qc_zip -maxdepth 1 -type f -name *.zip))
let n_zip=${#list_zip[@]}

echo -e "find $n_zip zipped files"

for ((i = 0; i <$n_zip; i++)); do
    file_name=`echo "${list_zip[$i]}" | cut -d'.' -f1`
    file_name=`basename ${file_name}`

    file_zip=$dir_bids_qc_zip/$file_name.zip
    file_html=$dir_bids_qc/$file_name.html
    flag_unzip=0
    if [ "$flag_continue" -eq "0" ]; then
        if test -f "$file_html"; then
            rm -rf "$file_html"
        fi
        echo -e "unzip $file_name"
        flag_unzip=1

    else
        if test -f "$file_html"; then
            continue
        else
            echo -e "unzip $file_name"
            flag_unzip=1
        fi
    fi
    # zipped files may contain absolute path
    # move data from the *.html layer
    if [ "$flag_unzip" -eq "1" ]; then
        echo $dir_bids_qc/$file_name"_temp"
        if test -d $dir_bids_qc/$file_name"_temp"; then
            rm -rf $dir_bids_qc/$file_name"_temp"
        fi
        mkdir -p $dir_bids_qc/$file_name"_temp"
        unzip -q $file_zip -d $dir_bids_qc/$file_name"_temp"
        file_html=$dir_bids_qc"/"$file_name"_temp"
        file_html=$(find "$file_html" -type f -name *.html)
        if test -f "$file_html"; then
            dir_html=`dirname ${file_html}`
            mv -f $dir_html/* $dir_bids_qc
        fi
        rm -rf $dir_bids_qc/$file_name"_temp"
    fi
done

echo -e "\nFinished unzip_BIDS_QC.sh: `date +%F-%H:%M:%S`\n"

