#!/bin/bash
# Holland Brown
# 2023-01-08
# Fix mask dir tree and copy ROI masks to main subject dirs

DataDir="/athena/victorialab/scratch/hob4003/study_EVO/NKI_MRI_data"
MasksDir="/athena/victorialab/scratch/hob4003/study_EVO/EVO_rest/EVO_rest_volumetric/HCP-MMP1_fsaverage_masks"
SubjectsList="/athena/victorialab/scratch/hob4003/study_EVO/NKI_MRI_data/NKIsublist.txt"

for i in $(cat "$SubjectsList"); do

    SUBJ=$(echo $i)
    echo -e "Cleaning $SUBJ files..."

    # Remove temporary text files created for vol parc
    if [ -f "$DataDir/$SUBJ.txt" ]; then
        rm "$DataDir/$SUBJ.txt"
    fi

    # Rename mask folders in masks dir to just be the subject ID
    if [ -d "$MasksDir/$SUBJ_HCP-MMP1_vol_roi_masks" ]; then
        mv "$MasksDir/$SUBJ_HCP-MMP1_vol_roi_masks" "$MasksDir/$SUBJ"
    fi

    # Make copy of ROI masks in subject's anat dir, rename subj anat masks dir, remove symbolic links from anat dir
    SubjectAnatDir="$DataDir"/"$SUBJ"/anat
    if [ ! -d "$MasksDir"/"$SUBJ" ]; then
        cp -rf "$MasksDir"/"$SUBJ" "$DataDir"/"$SUBJ"/anat
        mv "$DataDir"/"$SUBJ"/anat/"$SUBJ" "$DataDir"/"$SUBJ"/anat/"$SUBJ"_HCP-MMP1_vol_roi_masks
        rm -r "$DataDir"/"$SUBJ"/anat/T1w/$SUBJ/symlinks > /dev/null 2>&1
    fi

    # remove temp dirs from main subject dir
    rm -r "$DataDir/$SUBJ/label" > /dev/null 2>&1
    rm -r "$DataDir/$SUBJ/surf" > /dev/null 2>&1
    rm -r "$DataDir/$SUBJ/stats" > /dev/null 2>&1
    rm -r "$DataDir/$SUBJ/mri" > /dev/null 2>&1
    rm -r "$DataDir/$SUBJ/scripts" > /dev/null 2>&1
    rm -r "$DataDir/$SUBJ/symlinks" > /dev/null 2>&1
    rm -r "$DataDir/$SUBJ/tmp" > /dev/null 2>&1
    rm -r "$DataDir/$SUBJ/touch" > /dev/null 2>&1
    rm -r "$DataDir/$SUBJ/trash" > /dev/null 2>&1

    # If surface analysis files exist in ROI dirs, move them to new ROI surf dir
    ROIdir="$DataDir"/"$SUBJ"/func/rest/rois
    # echo -e "$ROIdir" # TEST

    # for all ROI dirs...
    for j in "$ROIdir"/*; do
        # echo -e "$j TEST 1" # TEST
        if [ -d $j ]; then # dirs only, not files
            # echo -e "$j TEST 2" # TEST
            if [ ! -d "$j/rest_lowerlev_surf" ]; then
                mkdir "$j/rest_lowerlev_surf"
            fi

            # move surface files from ROI dir to ROI surface lower level dir analysis
            for k in "$j"/*; do
                if [ -f "$k" ]; then
                    # echo -e "$k TEST 1" # TEST
                    if [[ "$k" == "$j"/"$SUBJ"*"_denoised_aggr"* ]]; then
                        # echo -e "$k TEST 2" # TEST
                        mv "$k" "$j/rest_lowerlev_surf"
                    fi
                fi
            done
        fi
    done

done

echo -e "Done."