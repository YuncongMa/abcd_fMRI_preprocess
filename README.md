# abcd_fMRI_process
A pipeline to process fMRI data in ABCD dataset

## Installation
1. Download this package
```
clone https://github.com/YuncongMa/abcd_fMRI_process.git
```

2. Create Conda environment
```
conda env create --name abcd
```

4. Install additional packages
```
pip install numpy bids nibabel
conda install -c conda-forge dcm2bids
conda install -c conda-forge dcm2niix
```

## Preprocessing Steps
### 1. Raw data to BIDS format
```
python abcd_dcm2bids_yuncong.py
```
### 2. fmriprep

### 3. XCP-D

### 4. Quality control

## Other Tools Included
ABCD-Study: abcd-dicom2bids https://github.com/ABCD-STUDY/abcd-dicom2bids/tree/master
