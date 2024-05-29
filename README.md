# abcd_fMRI_preprocess
A customizable pipeline to preprocess fMRI data in ABCD dataset, based on [abcd-dicom2bids](https://github.com/ABCD-STUDY/abcd-dicom2bids/tree/master), [fmriprep](https://github.com/nipreps/fmriprep), and [XCP-D](https://github.com/PennLINC/xcp_d)

## Installation
1. Download this package
```
clone https://github.com/YuncongMa/abcd_fMRI_process.git
```

2. Create Conda environment
```
conda create --name abcd python=3.8
```

3. Activate Conda environment
```
conda activate abcd
```

4. Install additional packages
```
pip install numpy bids nibabel
conda install -c conda-forge dcmtk
```
For Apple Silicon, use the homebrew to install dcmtk
```
brew install dcmtk
```
5. Install singularity
https://github.com/sylabs/singularity/releases

6. Add dcm2bids, dcmtk, fmriprep and xcp_d singularity images (.simg)
Check script /tool/download_simg.sh

## Preprocessing Steps
A main python script is used to generate bash scripts for processing ABCD dataset in a cluster environment.
There are three versions using different job scheduling function to control the large number of preprocessing jobs.
1. Use a batch job to control individual workflows. It is least dependent on the server system.
```
python abcd_fmri_preprocess_cluster.py
```
2. Use the array job function to do job scheduling on SGE system.
```
python abcd_fmri_preprocess_sge_array.py
```
3. Use the array job function to do job scheduling on SLURM system.
```
python abcd_fmri_preprocess_slurm_array.py
```

### 1. raw2bids.sh 
Convert raw data (*.tgz) to BIDS format (data in subfolders /anat/, /fmap/, /func/). Some imaging parameters are inserted based on vendors for future usage. One pair of field maps are selected automatically, but will need manual check for image artifacts or poor localization. Results will be saved in folder /BIDS with subfolder as sub-*/ses-*. Temporay files will be saved in folder /BIDS_Temp
### 2. bids_qc.sh 
Generate graphs for T1, T2, field map, fMRI images in HTML-based web pages. It supports manual QC labeling (unwanted images with be labeled in red boxes), outputing manual QC results in plain text files (image data names with labels as either pass or fail). Results will be saved in folder /BIDS_QC. Manual QC results can be saved in the /BIDS_QC replacing automatically generated files.
### 3. fmriprep.sh 
Run fmriprep on BIDS formatted MRI data with or without manual QC files. This step will perform a widely used fMRI preprocessing including slicing timing, distortion correction, motion correction, brain segmentation, and image registration. Results will be saved in folder /fmriprep, and temporary files will be saved in /fmriprep_work.
### 4. xcpd.sh 
Postprocess fMRI data to remove noises, including spatial smoothing, nuisance regression, temporal filtering. To get results in both NIFTI and CIFTI formats, two folders will be created (/xcpd and /xcpd_cifti). Temporary files will be saved into folder /xcpd_temp
### 5. collect.sh 
collect HTML-based reports from fmriprep and xcpd, as well as final preprocessed data. Results will be saved into folder /Result.

## Other Tools Included
### abcd-dicom2bids 
https://github.com/ABCD-STUDY/abcd-dicom2bids/tree/master
### dcmtk
https://dicom.offis.de/dcmtk.php.en
### fmriprep 
https://github.com/nipreps/fmriprep
### XCP-D 
https://github.com/PennLINC/xcp_d
