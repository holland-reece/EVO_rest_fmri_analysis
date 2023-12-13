#!/bin/bash
# Holland Brown
# 2023-12-13
# Fix mask dir tree and copy ROI masks to main subject dirs

DataDir="/athena/victorialab/scratch/hob4003/study_EVO/NKI_MRI_data"
MasksDir="/athena/victorialab/scratch/hob4003/study_EVO/EVO_rest/EVO_rest_volumetric/HCP-MMP1_fsaverage_masks"
SubjectsList="/athena/victorialab/scratch/hob4003/study_EVO/NKI_MRI_data/NKIsublist.txt"

for i in $(cat "$SubjectsList"); do

    SUBJ=$(echo $i)

    mv "$MasksDir/$SUBJ" "$MasksDir"/"$SUBJ"_HCP-MMP1_vol_roi_masks # rename the mask folders

    SubjectAnatDir="$DataDir"/"$SUBJ"/anat
    cp -rf "$MasksDir"/"$SUBJ"_HCP-MMP1_roi_vol_masks "$DataDir"/"$SUBJ"/anat # make copy of ROI masks in subject's anat dir

    rm -r "$DataDir"/"$SUBJ"/anat/T1w/$SUBJ/symlinks # remove symbolic links from anat dir

    # remove temp dirs from main subject dir
    rm -r "$DataDir/$SUBJ/label"
    rm -r "$DataDir/$SUBJ/surf"
    rm -r "$DataDir/$SUBJ/stats"
    rm -r "$DataDir/$SUBJ/mri"
    rm -r "$DataDir/$SUBJ/scripts"
    rm -r "$DataDir/$SUBJ/symlinks"
    rm -r "$DataDir/$SUBJ/tmp"
    rm -r "$DataDir/$SUBJ/touch"
    rm -r "$DataDir/$SUBJ/trash"

done