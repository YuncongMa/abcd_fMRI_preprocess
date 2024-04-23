#!/bin/sh

# Yuncong Ma
# This script is to submit an SGE array job for processing ABCD dataset
# bash {$file_submit_sge_array$}
# created on {$date_time$}

# directory for scripts, temporary folder of each step
dir_script_cluster={$dir_script_cluster$}
# log folder
dir_log=$dir_script_cluster/log_array_job

# clean up previous log files
if [[ ! -d "$dir_log" ]]; then
    mkdir -p $dir_log
else
    rm -rf $dir_log/*
fi

cd $dir_log

# submit SGE array job

{$submit_command$}