#! /bin/bash

# Yuncong Ma, 3/22/2024
# Convert raw data in ABCD dataset to BIDS format
# This bash file does NOT process DTI or task fMRI data
#
# This code is adapted from the toolbox abcd-dicom2bids (https://github.com/DCAN-Labs/abcd-dicom2bids)
#
# Major updates include:
# support for new configuration file requirement in dcm2niix,
# updated field map phase encoding key for fmriprep,
# insert of missing slicing timing information for some fMRI data,
# python version of field map selection
#
# Additional notes:
# this code is designed specifically for ABCD release 5.0. Different releases may use different
# file names or contain different information.
# This code is not compatible to other datasets using different protocols.

# For use as a function
parse()
{
   # Default setting
   subject=
   session=
   dir_bids=
   dir_temp_sub=
   dir_abcd_raw2bids=
   file_dcm2bids=
   list_sub_scan=
   file_log='./Log_raw2bids.log'

    while [ -n "$1" ];
    do
        case $1 in
            --subject)
                subject=$2;
            shift 2;;
            --session)
                session=$2;
            shift 2;;
            --bids)
                dir_bids=$2;
            shift 2;;
            --tempDir)
                dir_temp_sub=$2;
            shift 2;;
            --abcd_raw2bids)
                dir_abcd_raw2bids=$2;
            shift 2;;
            --dcm2bids)
                file_dcm2bids=$2;
            shift 2;;
            --scanList)
                list_sub_scan=$2;
            shift 2;;
            --log)
                file_log=$2;
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

# Start bash processing

echo -e "\nStart to running raw2bids" 
echo -e "Start time : `date +%F-%H:%M:%S`\n" 

# Print out input parameters
echo -e "subject = "$subject 
echo -e "session = "$session 
echo -e "dir_bids = "$dir_bids 
echo -e "dir_temp_sub = "$dir_temp_sub 
echo -e "dir_abcd_raw2bids = "$dir_abcd_raw2bids 
echo -e "list_sub_scan = "$list_sub_scan

# add prefix for BIDS format
subject_id='sub-'$subject
session_id='ses-'$session

dir_abcd_dicom2bids=$dir_abcd_raw2bids'/abcd-dicom2bids'

System=$(uname -s)

#date
#hostname
#echo ${SLURM_JOB_ID}

# Setup scratch space directory
if [ ! -d ${dir_temp_sub} ]; then
    mkdir -p ${dir_temp_sub}
    # chown :fnl_lab ${dir_temp_sub} || true
    chmod 770 ${dir_temp_sub} || true
fi

# copy all tgz to the scratch space dir
echo `date`" :COPYING TGZs TO SCRATCH: ${dir_temp_sub}"  
#cp ${TGZDIR}/* ${dir_temp_sub}
while IFS= read -r line; do
    # Remove leading and trailing whitespace
    line=$(echo "$line" | xargs)
    # Copy the file to the destination directory
    cp "$line" "$dir_temp_sub"
done < "$list_sub_scan"



# unpack tgz to ABCD_DCMs directory
mkdir ${dir_temp_sub}/DCMs
echo `date`" :UNPACKING DCMs: ${dir_temp_sub}/DCMs" 
for tgz in ${dir_temp_sub}/*.tgz; do
    echo $tgz 
    tar -xzf ${tgz} -C ${dir_temp_sub}/DCMs
done

if [ -e ${dir_temp_sub}/DCMs/${subject_id}/${session_id}/func ]; then
    python ${dir_abcd_dicom2bids}/src/remove_RawDataStorage_dcms.py \
    ${dir_temp_sub}/DCMs/${subject_id}/${session_id}/func \
    
fi


# convert DCM to BIDS and move to ABCD directory
mkdir ${dir_temp_sub}/BIDS_unprocessed
cp ${dir_abcd_raw2bids}/dataset_description.json ${dir_temp_sub}/BIDS_unprocessed/

echo `date`" :RUNNING dcm2bids"
# dcm2bids can be run in singularity based on file_dcm2bids or locally installed version
if test -f "$file_dcm2bids"; then
    singularity run "$file_dcm2bids" dcm2bids -d ${dir_temp_sub}/DCMs/${subject_id} \
     -p ${subject} \
     -s ${session} \
     -c ${dir_abcd_raw2bids}/abcd_dcm2bids.conf \
     -o ${dir_temp_sub}/BIDS_unprocessed \
     --force_dcm2bids --clobber
else
    dcm2bids -d ${dir_temp_sub}/DCMs/${subject_id} \
     -p ${subject} \
     -s ${session} \
     -c ${dir_abcd_raw2bids}/abcd_dcm2bids.conf \
     -o ${dir_temp_sub}/BIDS_unprocessed \
     --force_dcm2bids --clobber
fi
 

# correct volume order for fMRI data
if [[ -e ${dir_temp_sub}/BIDS_unprocessed/${subject_id}/${session_id}/func ]]; then
    echo `date`" :CHECKING BIDS ORDERING OF EPIs" 
    i=0
    while [ "`python ${dir_abcd_dicom2bids}/src/run_order_fix.py ${dir_temp_sub}/BIDS_unprocessed ${dir_temp_sub}/bids_order_error.json ${dir_temp_sub}/bids_order_map.json --all --subject ${subject_id}`" != ${subject_id} ] && [ $i -ne 3 ]; do
        ((i++))
        echo `date`" :  WARNING: BIDS functional scans incorrectly ordered. Attempting to reorder. Attempt #$i" 
    done
    if [ "`python ${dir_abcd_dicom2bids}/src/run_order_fix.py ${dir_temp_sub}/BIDS_unprocessed ${dir_temp_sub}/bids_order_error.json ${dir_temp_sub}/bids_order_map.json --all --subject ${subject_id}`" == ${subject_id} ]; then
        echo `date`" : BIDS functional scans correctly ordered" 
    else
        echo `date`" :  ERROR: BIDS incorrectly ordered even after running run_order_fix.py" 
        # exit
    fi
fi

# select best fieldmap and update sidecar jsons
echo `date`" :RUNNING SEFM SELECTION AND EDITING SIDECAR JSONS" 
if [ -d ${dir_temp_sub}/BIDS_unprocessed/${subject_id}/${session_id}/fmap ]; then
    python ${dir_abcd_raw2bids}/sefm_eval_and_json_editor_yuncong.py \
     ${dir_temp_sub}/BIDS_unprocessed \
     ${FSL_DIR} \
     --participant-label=${subject} \
     --output_dir \
     $dir_bids \
     
fi

#rm ${dir_temp_sub}/BIDS_unprocessed/${subject_id}/${session_id}/fmap/*dir-both* 2> /dev/null || true


# Fix all json extra data errors
for j in ${dir_temp_sub}/BIDS_unprocessed/${subject_id}/${session_id}/*/*.json; do
    mv ${j} ${j}.temp
    # print only the valid part of the json back into the original json
    jq '.' ${j}.temp > ${j}
    rm ${j}.temp
done


echo `date`" :COPYING BIDS DATA BACK: ${dir_bids}" 

TEMPBIDSINPUT=${dir_temp_sub}/BIDS_unprocessed/${subject_id}
if [ -d ${TEMPBIDSINPUT} ] ; then
    echo `date`" :CHMOD BIDS INPUT" 
    if [ "$System" == "Linux" ]; then
      chmod g+rw -R ${TEMPBIDSINPUT} || true
    fi
    echo `date`" :COPY BIDS INPUT" 
    mkdir -p ${dir_bids}
    cp -r ${TEMPBIDSINPUT} ${dir_bids}/
fi

ROOT_SRCDATA=${dir_bids}/sourcedata
TEMPSRCDATA=${dir_temp_sub}/BIDS_unprocessed/sourcedata/${subject_id}
if [ -d ${TEMPSRCDATA} ] ; then
    echo `date`" :CHMOD SOURCEDATA" 
    if [ "$System" == "Linux" ]; then
      chmod g+rw -R ${TEMPSRCDATA} || true
    fi
    echo `date`" :COPY SOURCEDATA" 
    mkdir -p ${ROOT_SRCDATA}
    cp -r ${TEMPSRCDATA} ${ROOT_SRCDATA}/
fi

# correct json files in BIDS folder
python $dir_abcd_raw2bids'/correct_jsons.py' \
  -bids $dir_bids \
  -subject $subject \
  -session $session \

# remove dir-both
find $dir_bids/$subject_id/$session_id -name *dir-both* -delete

echo -e "Finished at `date +%F-%H:%M:%S`\n" 
