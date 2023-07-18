#!/bin/bash

# Run Feat Analyses on Local Machine Instead of HDD

# Reading and writing to an external disk is time-consuming, especially if the disk is
# around 80% full. As the EVO analyses progress and the external HD fills up, this script
# can help organize analysis directories on my local machine and transfer them to the
# disk at the end.


#-----------------------
# Set paths and env vbls
#-----------------------

ROI="R_MFG"
MY_LOCAL_DIR=/home/holland/Desktop/temp_datadir # where you want temporary subject dirs to be made
HD_DATADIR=/media/holland/LACIE-SHARE/EVO_MRI_data # where subject dirs exist on the hard drive
FEATFOLDER=lower_level_remean.feat

SUBJECTLIST=/home/holland/Desktop/${ROI}_subs2run.txt # path/to/subjectlist.txt

# MY_ENV=/home/holland/anaconda3/envs/py311 # path to this project's anaconda environment
# export PATH=$MY_ENV:$PATH


#-------------------------------------------------------------------
# Create local directories and copy preprocessed resting state files
#-------------------------------------------------------------------

sublist=`cat ${SUBJECTLIST}` # read subject list

# make local data dir if it doesn't already exist and navigate to that dir
# [ -d ${MY_LOCAL_DIR} ] && echo "Local data directory exists." || mkdir ${MY_LOCAL_DIR}
# cd ${MY_LOCAL_DIR} # navigate to data dir on local machine

# for sub in ${sublist}
# do
#     HD_SUBDIR=${HD_DATADIR}/${sub}/${sub}_rest_afni_results_ICA

#     # make local subject directory and subject roi dir
#     mkdir ${MY_LOCAL_DIR}/${sub} # make local subject dir
#     mkdir ${MY_LOCAL_DIR}/${sub}/${ROI} # make local roi subj dir

#     if [[ ! -e ${MY_LOCAL_DIR}/${sub}/${sub}_remean_fanat.nii.gz ]] # if local remeaned file does not exist...
#     then
#     # if nifti file exists on HDD, copy nifti file to local machine
#     [ -e ${HD_SUBDIR}/${sub}_remean_fanat.nii.gz ] && cp ${HD_SUBDIR}/${sub}_remean_fanat.nii.gz ${MY_LOCAL_DIR}/${sub} || [ -e ${HD_SUBDIR}/${sub}_fanaticor.nii.gz ] cp ${HD_SUBDIR}/${sub}_fanaticor.nii.gz ${MY_LOCAL_DIR}/${sub} || cp ${HD_SUBDIR}/errts.{${sub}.fanaticor+tlrc.BRIK,${sub}.fanaticor+tlrc.HEAD} ${MY_LOCAL_DIR}/${sub}
#     fi

# done

#-----------------------------------------------------------
# Check if ROI dir already exists on HDD for each subject...
#-----------------------------------------------------------

# for sub in ${sublist}
# do

#     HD_ROI_SUBDIR=${HD_DATADIR}/${sub}/${sub}
#     LOCAL_ROI_DIR=${MY_LOCAL_DIR}/${sub}/${ROI}

#     [ -d ${HD_ROI_SUBDIR} ] && echo ${sub}

# done

#-----------------------------------
# Move local roi folders over to HDD
#-----------------------------------

# for sub in ${sublist}
# do

#     HD_SUBDIR=${HD_DATADIR}/${sub}
#     LOCAL_ROI_DIR=${MY_LOCAL_DIR}/${sub}/${ROI}

#     [ -d ${LOCAL_ROI_DIR} ] && mv ${LOCAL_ROI_DIR} ${HD_SUBDIR} || mv ${LOCAL_ROI_DIR}/${FEATFOLDER} ${HD_SUBDIR}/${roi}
#     echo "Moving ${ROI} files for subject ${sub}..."

# done
# echo "Done."