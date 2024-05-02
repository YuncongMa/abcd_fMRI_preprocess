#!/bin/bash
# Yuncong Ma, 4/30/2024
# move results in BIDS_QC to a different folder if they have corresponding manual BIDS QC files

echo -e "\nStart move_manual_BIDS_QC.sh: `date +%F-%H:%M:%S`\n"

# directories for storing zipped BIDS_QC results
dir_bids_qc=/Volumes/Crucial_4TB/ABCD/BIDS_QC
dir_bids_qc_checked=/Volumes/Crucial_4TB/ABCD/BIDS_QC_checked
dir_bids_qc_manual=/Volumes/Crucial_4TB/ABCD/manual_BIDS_QC_YuncongMa

# create folder
if [[ ! -d "dir_bids_qc_checked" ]]; then
    mkdir -p $dir_bids_qc_checked
fi

# find manual BIDS QC files
list_manual_BIDS_QC=($(find $dir_bids_qc_manual -maxdepth 1 -type f -name "sub*.txt"))
let n_manual_BIDS_QC=${#list_manual_BIDS_QC[@]}
echo $n_manual_BIDS_QC

for ((i = 0; i < $n_manual_BIDS_QC; i++)); do
    file_txt=$(basename ${list_manual_BIDS_QC[i]})
    basename_QC=$(echo "$file_txt" | sed 's/\.txt$//')
#    echo $basename_QC
    file_html=$dir_bids_qc"/"$basename_QC".html"
#    echo $file_html
    if test -f $file_html; then
        echo -e "move $basename_QC"
        mv "$file_html" "$dir_bids_qc_checked/"
        mv "$dir_bids_qc/$basename_QC.txt" "$dir_bids_qc_checked/"
        mv -f "$dir_bids_qc/$basename_QC" "$dir_bids_qc_checked/"
    else
        echo -e "skip $basename_QC"
    fi
done

echo -e "\nFinish : `date +%F-%H:%M:%S`\n"
