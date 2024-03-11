#!/bin/sh

# This bash script is to run collect.sh
# The script is generated based on the toolbox abcd_fmri_preprocess (/template/template_collect.sh)
# created on {$date_time$}

# Use command to submit this job:
# $ {$job_submit_command$}

echo -e "Start collect at `date +%F-%H:%M:%S`\n"

flag_cluster={$flag_cluster$}

subject={$subject$}
session={$session$}

# folder to store results
dir_failed={$dir_failed$}/sub-$subject"_ses-"$session
dir_result={$dir_result$}/sub-$subject"_ses-"$session

# start to check each step
flag=0

# check raw2bids
# directory of BIDS folder
dir_bids={$dir_bids$}/sub-$subject/ses-$session
dir_bids_temp={$dir_bids_temp$}/sub-$subject/ses-$session

if test -d "$dir_bids"; then
    let spaceUse=$(df -k $dir_bids/ | tail -1 | awk '{print $4}')
    let spaceUse=$spaceUse/1024  # MB
    if [ "$spaceUse" -ls "100" ]; then
        echo 'raw2bids failed\n'
        flag=1
    fi
fi
if test -d "$dir_bids_temp"; then
    let spaceUse=$(df -k $dir_bids_temp/ | tail -1 | awk '{print $4}')
    let spaceUse=$spaceUse/1024  # MB
    if [ "$spaceUse" -ls "100" ]; then
        flag=1
    fi
fi

# check fmriprep
# directory for fmriprep
dir_fmriprep={$dir_fmriprep$}/sub-$subject
dir_fmriprep_work_sub={$dir_fmriprep_work_sub$}

if test -d "$dir_fmriprep";then
    let spaceUse=$(df -k $dir_fmriprep/ | tail -1 | awk '{print $4}')
    let spaceUse=$spaceUse/1024  # MB
    if [ "$spaceUse" -ls "100" ];then
        echo 'fmriprep failed\n'
        flag=1
    fi
fi
if test -d "$dir_fmriprep_work_sub";then
    let spaceUse=$(df -k $dir_fmriprep_work_sub/ | tail -1 | awk '{print $4}')
    let spaceUse=$spaceUse/1024  # MB
    if [ "$spaceUse" -ls "100" ]; then
        flag=1
    fi
fi

# check xcpd
# directory of the xcpd output folder
dir_xcpd={$dir_xcpd$}/sub-$subject
dir_xcpd_cifti={$dir_xcpd_cifti$}/sub-$subject
dir_xcpd_work_sub={$dir_xcpd_work_sub$}

if test -d "$dir_fmriprep_work_sub";then
    let spaceUse=$(df -k $dir_xcpd/ | tail -1 | awk '{print $4}')
    let spaceUse=$spaceUse/1024  # MB
    if [ "$spaceUse" -ls "100" ]; then
        echo 'dir_xcpd failed\n'
        flag=1
    fi
else
    flag=1
fi
if test -d "$dir_xcpd_cifti";then
    let spaceUse=$(df -k $dir_xcpd_cifti/ | tail -1 | awk '{print $4}')
    let spaceUse=$spaceUse/1024  # MB
    if [ "$spaceUse" -ls "100" ]; then
        flag=1
    fi
else
    flag=1
fi
if test -d "$dir_xcpd_work_sub";then
    let spaceUse=$(df -k $dir_xcpd_work_sub/ | tail -1 | awk '{print $4}')
    let spaceUse=$spaceUse/1024  # MB
    if [ "$spaceUse" -ls "100" ]; then
        flag=1
    fi
fi

# move to folder if failed
flag=0  # for test
if [ "$flag" -eq "1" ]; then
    mkdir -p "$dir_failed/fmriprep"
    mkdir -p "$dir_failed/xcpd"
    mkdir -p "$dir_failed/xcpd_cifti"
    if test -d "$dir_fmriprep"; then
        mv "$dir_fmriprep/*" "$dir_failed/fmriprep/"
    fi
    if test -d "$dir_xcpd"; then
        mv "$dir_xcpd/*" "$dir_failed/xcpd/"
    fi
    if test -d "$dir_xcpd_cifti"; then
        mv "$dir_xcpd_cifti/*" "$dir_failed/xcpd_cifti/"
    fi
    # delete temporary files
    if [ test -d "$dir_fmriprep_work_sub" ]; then
        rm -rf "$dir_fmriprep_work_sub"
    fi
    if [ test -d "$dir_xcpd_work_sub" ]; then
        rm -rf "$dir_xcpd_work_sub"
    fi
else
    # move HTML-based reports from fmriprep and xcpd
    mkdir -p $dir_result
    # fmriprep report
    if [ "$flag_cluster" -eq "1" ]; then
        rcp -r "$dir_fmriprep/figures" "$dir_result/fmriprep_figures"
        rcp -r "$dir_fmriprep.html" "$dir_result/fmriprep_report.html"
    else
        cp -r "$dir_fmriprep/figures" "$dir_result/fmriprep_figures"
        cp -r "$dir_fmriprep.html" "$dir_result/fmriprep_report.html"
    fi
    # change contents in the HTML for new file organization
    html_content=$(cat "$dir_result/fmriprep_report.html")
    html_content=$(echo "$html_content" | sed "s/sub-${subject}\/figures/fmriprep_figures/g")
    output_file=$dir_result"/fmriprep_report.html"
    echo "$html_content" > "$output_file"

    # xcpd report
    if [ "$flag_cluster" -eq "1" ]; then
        rcp -r "$dir_xcpd" "$dir_result/xcpd"
        rcp -r "$dir_xcpd_cifti" "$dir_result/xcpd_cifti"
    else
        cp -r "$dir_xcpd" "$dir_result/xcpd"
        cp -r "$dir_xcpd_cifti" "$dir_result/xcpd_cifti"
    fi

    # final fmri results for subsequent analyses

    # additional data for controlling motion and other physiology
fi

echo -e "Finish collect at `date +%F-%H:%M:%S`\n"

