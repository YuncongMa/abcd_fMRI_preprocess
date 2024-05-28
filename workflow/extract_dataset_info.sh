#!/bin/bash
# Yuncong Ma, 5/15/2024
# Get scan info in ABCD dataset
# bash /cbica/home/mayun/Projects/ABCD/Script/workflow/extract_scan_info.sh dir_raw_data dir_dataset_info

parse()
{
    # Default setting
    dir_raw_data=
    file_dataset_info=
    extension=*.tgz
    
    while [ -n "$1" ];
    do
        case $1 in
            --raw)
                dir_raw_data=$2;
            shift 2;;
            --file-info)
                file_dataset_info=$2;
            shift 2;;
            --extension)
                extension=$2;
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

find $dir_raw_data -maxdepth 3 -type f -name $extension > $file_dataset_info




