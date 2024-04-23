#!/bin/bash
# Yuncong Ma, 4/16/2024
# Get scan info in ABCD dataset
# bash /cbica/home/mayun/Projects/ABCD/Script/workflow/extract_scan_info.sh dir_raw_data dir_dataset_info

parse()
{
    # Default setting
    dir_raw_data=
    dir_dataset_info=
    
    while [ -n "$1" ];
    do
        case $1 in
            --raw)
                dir_raw_data=$2;
            shift 2;;
            --dir-info)
                dir_dataset_info=$2;
            shift 2;;
            -*)
                echo "ERROR:no such option $1"
            exit;;
            *)
            break;;
        esac
    done
}

parse $*

mkdir -p $dir_dataset_info

find $dir_raw_data -maxdepth 3 -type f -name *.tgz > $dir_dataset_info/List_all_tgz.txt




