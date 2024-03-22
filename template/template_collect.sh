#!/bin/sh

# This bash script is to run collect.sh
# The script is generated based on the toolbox abcd_fmri_preprocess (/template/template_collect.sh)
# created on {$date_time$}

# Use command to submit this job:
# $ {$job_submit_command$}

echo -e "Start collect at `date +%F-%H:%M:%S`\n"

# subject
subject={$subject$}
session={$session$}
folder_label="sub-"$subject"_ses-"$session

# script folder
dir_script_cluster={$dir_script_cluster$}
dir_script_cluster_sub=$dir_script_cluster/$folder_label

# folder to store results
dir_failed={$dir_failed$}/$folder_label
dir_result={$dir_result$}/$folder_label

# template of final report
file_template={$file_template$}

# directory of BIDS folder
dir_bids={$dir_bids$}
dir_bids_sub=$dir_bids"/sub-"$subject"/ses-"$session
dir_bids_work={$dir_bids_work$}
dir_bids_work_sub=$dir_bids_work/$folder_label

# directory for fmriprep
dir_fmriprep={$dir_fmriprep$}
dir_fmriprep_work={$dir_fmriprep_work$}
dir_fmriprep_sub=$dir_fmriprep/$folder_label
dir_fmriprep_work_sub=$dir_fmriprep_work/$folder_label

# directory of the xcpd output folder
dir_xcpd={$dir_xcpd$}
dir_xcpd_cifti={$dir_xcpd_cifti$}
dir_xcpd_work={$dir_xcpd_work$}
dir_xcpd_sub=$dir_xcpd/$folder_label
dir_xcpd_cifti_sub=$dir_xcpd_cifti/$folder_label
dir_xcpd_work_sub=$dir_xcpd_work/$folder_label

# start to check each step
flag=0
flag_fmriprep=0
flag_xcpd=0

# whether to clean up all intermediate files
flag_cleanup=1

# check raw2bids
if test -d "$dir_bids_sub"; then
    let spaceUse=$(df -m $dir_bids_sub/ | tail -1 | awk '{print $4}')
    if [ "$spaceUse" -lt "100" ]; then
        echo 'raw2bids failed\n'
        flag=1
    fi
fi
if test -d "$dir_bids_work_sub"; then
    let spaceUse=$(df -m $dir_bids_work_sub/ | tail -1 | awk '{print $4}')
    if [ "$spaceUse" -lt "100" ]; then
        flag=1
    fi
fi

# check fmriprep
if test -d "$dir_fmriprep_sub";then
    let spaceUse=$(df -m $dir_fmriprep_sub/ | tail -1 | awk '{print $4}')
    if [ "$spaceUse" -lt "100" ]; then
        echo 'fmriprep failed\n'
        flag=1
    fi
fi
if test -d "$dir_fmriprep_work_sub";then
    let spaceUse=$(df -m $dir_fmriprep_work_sub/ | tail -1 | awk '{print $4}')
    if [ "$spaceUse" -lt "100" ]; then
        flag=1
    fi
fi
# check HTML-based report
if test -f "$dir_fmriprep_sub.html"; then
    html_content=$(cat "$dir_fmriprep_sub.html")
    if [[ "$html_content" == *"No errors to report!"* ]]; then
        echo "No errors in fmriprep"
    else
        flag_fmriprep=1
        flag=1
    fi
else
    flag=1
fi

# check xcpd
if test -d "$dir_fmriprep_work_sub";then
    let spaceUse=$(df -m $dir_fmriprep_work_sub/ | tail -1 | awk '{print $4}')
    if [ "$spaceUse" -lt "100" ]; then
        echo 'dir_xcpd failed\n'
        flag=1
    fi
else
    flag=1
fi
if test -d "$dir_xcpd_cifti_sub";then
    let spaceUse=$(df -m $dir_xcpd_cifti_sub/ | tail -1 | awk '{print $4}')
    if [ "$spaceUse" -lt "100" ]; then
        flag=1
    fi
else
    flag=1
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
    if test -f "$dir_fmriprep_sub/sub-$subject.html"; then
        cp -r "$dir_fmriprep_sub/sub-$subject/figures" "$dir_result/fmriprep_figures"
        cp -r "$dir_fmriprep_sub/sub-$subject.html" "$dir_result/fmriprep_report.html"
        # change contents in the HTML for new file organization
        html_content=$(cat "$dir_result/fmriprep_report.html")
        html_content=$(echo "$html_content" | sed "s/sub-${subject}\/figures/fmriprep_figures/g")
        output_file=$dir_result"/fmriprep_report.html"
        echo "$html_content" > "$output_file"
    fi

    # xcpd report
    if test -f "$dir_xcpd_sub/xcp_d/sub-$subject.html"; then
        cp -r "$dir_xcpd_sub/xcp_d/sub-$subject/figures" "$dir_result/xcpd_figures"
        cp -r "$dir_xcpd_sub/xcp_d/sub-$subject.html" "$dir_result/xcpd_report.html"
        cp -r "$dir_xcpd_cifti_sub/xcp_d/sub-$subject/figures" "$dir_result/xcpd_cifti_figures"
        cp -r "$dir_xcpd_cifti_sub/xcp_d/sub-$subject.html" "$dir_result/xcpd_cifti_report.html"
        # change contents in the HTML for new file organization
        html_content=$(cat "$dir_result/xcpd_report.html")
        html_content=$(echo "$html_content" | sed "s/sub-${subject}\/figures/xcpd_figures/g")
        output_file=$dir_result"/xcpd_report.html"
        echo "$html_content" > "$output_file"
        html_content=$(cat "$dir_result/xcpd_cifti_report.html")
        html_content=$(echo "$html_content" | sed "s/sub-${subject}\/figures/xcpd_cifti_figures/g")
        output_file=$dir_result"/xcpd_cifti_report.html"
        echo "$html_content" > "$output_file"
    fi

    # final fmri results for subsequent analyses
    # html_content=$(cat "$file_template")
    # html_content=$(echo "$html_content" | sed "s/{\$subject$}/$subject/g")
    # html_content=$(echo "$html_content" | sed "s/{\$session$}/$session/g")
    # if [ "$flag" -eq "0" ]; then
    #     html_content=$(echo "$html_content" | sed "s/{\$session$}/$session/g")
    # output_file=$dir_result"/report.html"
    # echo "$html_content" > "$output_file"
    # additional data for controlling motion and other physiology

    # move preprocessed results and other essential files
    mkdir -p "$dir_result/result_vol"
    mkdir -p "$dir_result/result_cifti"
    file_name_tag=
    file_name_tag[0]='motion'
    file_name_tag[1]='outliers'
    file_name_tag[2]='desc-denoisedSmoothed_bold'
    for j in $(seq 0 2)
    do
        tag="*"${file_name_tag[j]}"*"
        cp -p $(find "$dir_xcpd_sub/xcp_d/sub-$subject/ses-$session/func" -name $tag) "$dir_result/result_vol"
        cp -p $(find "$dir_xcpd_cifti_sub/xcp_d/sub-$subject/ses-$session/func" -name $tag) "$dir_result/result_cifti"
    done

    # copy log files from Script_Cluster
    mkdir -p "$dir_result/log"
    cp -p $(find "$dir_script_cluster_sub" -name "*Log*") "$dir_result/log"


    # cleanout result folder in fmriprep, XCP_D and XCP_D_cifti
    if [ "$flag_cleanup" -eq "1" ]; then
        # raw2bids
        if test -d "$dir_bids_work_sub";then
            echo 'remove temp file in raw2bids which uses'
            du -sh $dir_bids_work_sub
            rm -rf $dir_bids_work_sub
        fi
        # fmriprep
        if test -d "$dir_fmriprep_sub";then
            echo 'remove temp file in fmriprep which uses'
            du -sh $dir_fmriprep_sub
            rm -rf $dir_fmriprep_sub
        fi
        if test -d "$dir_fmriprep_work_sub";then
            echo 'remove temp file in fmriprep work which uses'
            du -sh $dir_fmriprep_work_sub
            rm -rf $dir_fmriprep_work_sub
        fi
        # xcpd
        if test -d "$dir_xcpd_sub";then
            echo 'remove temp file in xcpd which uses'
            du -sh $dir_xcpd_sub
            rm -rf $dir_xcpd_sub
        fi
        if test -d "$dir_xcpd_cifti_sub";then
            echo 'remove temp file in xcpd cifti which uses'
            du -sh $dir_xcpd_cifti_sub
            rm -rf $dir_xcpd_cifti_sub
        fi
        if test -d "$dir_xcpd_work_sub";then
            echo 'remove temp file in xcpd work which uses'
            du -sh $dir_xcpd_work_sub
            rm -rf $dir_xcpd_work_sub
        fi
        echo 'cleaned out all intermediate files'
    fi
    
fi

echo -e "Finish collect at `date +%F-%H:%M:%S`\n"

