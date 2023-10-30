#!/bin/bash
# EVO resting-state lower level analysis: ROI-to-wholebrain correlation
# Holland Brown
# Updated 2023-10-30

# ---------------------- Important User-Defined Parameters ----------------------

StudyFolder=$1 # location of Subject folder
Subject=$2 # space delimited list of subject IDs
NTHREADS=$3 # set number of threads; larger values will reduce runtime (but also increase RAM usage)
StartSession=$4

RunICAAROMA=true # Motion correction and artifact identification with ICA-AROMA (run this for EVO participants)
RunMGTR=false # NOTE: PIs decided not to run MGTR script for EVO study (see Chuck's papers on gray-ordinates for more info)
Vol2FirstSurf=true # project denoised volumes onto a surface
SmoothVol2SecondSurf=true # additional 1.75 mm smoothing before projecting onto a second surface

# Set directories to scripts and CiftList text files
MEDIR="/athena/victorialab/scratch/hob4003/ME_Pipeline/MEF-P-HB/MultiEchofMRI-Pipeline" # main pipeline scripts dir
AromaPyDir="/athena/victorialab/scratch/hob4003/ME_Pipeline/ICA-AROMA-master" # path to original ICA-AROMA install dir (where ICA_AROMA.py is located)
CiftiConfigDir="$MEDIR/EVO_config" # CIFTI config dir (where CiftiList text files are saved)
KernelSize="$CiftiConfigDir"/KernelSize.txt # dimensions of kernel (cm) for smoothing/projection onto surface; can list multiple sizes and see which is better?
FSDir="$MEDIR/res0urces/FS" # dir with FreeSurfer (FS) atlases 
FSLDir="$MEDIR/res0urces/FSL" # dir with FSL (FSL) atlases

# ---------------------- Environment Setup ----------------------

module load python
module load Connectome_Workbench/1.5.0/Connectome_Workbench