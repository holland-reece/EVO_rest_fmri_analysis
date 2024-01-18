#!/bin/bash
# Holland Brown
# Updated 2023-01-10
# Remove symbolic links and copy files they link to into surf dir before running create_subj_volume_parcellation.sh

SUBJECTS_DIR="/athena/victorialab/scratch/hob4003/study_EVO/NKI_MRI_data" # main data dir, where subject dirs are located
SubjectsList="$SUBJECTS_DIR/NKI_subjectlist.txt"

for i in $(cat "$SubjectsList"); do

    SUBJ=$(echo $i)
    echo "    ---------------------    $SUBJ    ---------------------    "

    SubFreeSurferDir="$SUBJECTS_DIR"/"$SUBJ"/anat/T1w/"$SUBJ"
    SubSurfDir="$SubFreeSurferDir"/surf

    # Make dir for symlinks if necessary
    if [ ! -d "$SubFreeSurferDir/symlinks" ]; then
        mkdir "$SubFreeSurferDir/symlinks"
    else
        echo -e "$SubFreeSurferDir/symlinks already exists..."
    fi

    # Replace Left Pial symbolic link with file it points to
    if [ ! -f "$SubFreeSurferDir/symlinks/lh.pial" ]; then
        mv "$SubSurfDir/lh.pial" "$SubFreeSurferDir/symlinks"
        cp "$SubSurfDir/lh.pial.rawavg.conf" "$SubFreeSurferDir"
        mv "$SubFreeSurferDir/lh.pial.rawavg.conf" "$SubSurfDir/lh.pial"
    else
        echo -e "$SUBJ lh.pial already exists." # check
    fi

    # Replace Left White symbolic link with file it points to
    if [ ! -f "$SubFreeSurferDir/symlinks/lh.white" ]; then
        mv "$SubSurfDir/lh.white" "$SubFreeSurferDir/symlinks"
        cp "$SubSurfDir/lh.white.rawavg.conf" "$SubFreeSurferDir"
        mv "$SubFreeSurferDir/lh.white.rawavg.conf" "$SubSurfDir/lh.white"
    else
        echo -e "$SUBJ lh.white already exists." # check
    fi

    # Replace Left White.H symbolic link with file it points to
    if [ ! -f "$SubFreeSurferDir/symlinks/lh.white.H" ]; then
        mv "$SubSurfDir/lh.white.H" "$SubFreeSurferDir/symlinks"
        cp "$SubSurfDir/lh.white.preaparc.H" "$SubFreeSurferDir"
        mv "$SubFreeSurferDir/lh.white.preaparc.H" "$SubSurfDir/lh.white.H"
    else
        echo -e "$SUBJ lh.white.H already exists." # check
    fi

    # Replace Left White.K symbolic link with file it points to
    if [ ! -f "$SubFreeSurferDir/symlinks/lh.white.K" ]; then
        mv "$SubSurfDir/lh.white.K" "$SubFreeSurferDir/symlinks"
        cp "$SubSurfDir/lh.white.preaparc.K" "$SubFreeSurferDir"
        mv "$SubFreeSurferDir/lh.white.preaparc.K" "$SubSurfDir/lh.white.K"
    else
        echo -e "$SUBJ lh.white.K already exists." # check
    fi

    # Replace Right Pial symbolic link with file it points to
    if [ ! -f "$SubFreeSurferDir/symlinks/rh.pial" ]; then
        mv "$SubSurfDir/rh.pial" "$SubFreeSurferDir/symlinks"
        cp "$SubSurfDir/rh.pial.rawavg.conf" "$SubFreeSurferDir"
        mv "$SubFreeSurferDir/rh.pial.rawavg.conf" "$SubSurfDir/rh.pial"
    else
        echo -e "$SUBJ rh.pial already exists." # check
    fi

    # Replace Right White symbolic link with file it points to
    if [ ! -f "$SubFreeSurferDir/symlinks/rh.white" ]; then
        mv "$SubSurfDir/rh.white" "$SubFreeSurferDir/symlinks"
        cp "$SubSurfDir/rh.white.rawavg.conf" "$SubFreeSurferDir"
        mv "$SubFreeSurferDir/rh.white.rawavg.conf" "$SubSurfDir/rh.white"
    else
        echo -e "$SUBJ rh.white already exists." # check
    fi

    # Replace Right White.H symbolic link with file it points to
    if [ ! -f "$SubFreeSurferDir/symlinks/rh.white.H" ]; then
        mv "$SubSurfDir/rh.white.H" "$SubFreeSurferDir/symlinks"
        cp "$SubSurfDir/rh.white.preaparc.H" "$SubFreeSurferDir"
        mv "$SubFreeSurferDir/rh.white.preaparc.H" "$SubSurfDir/rh.white.H"
    else
        echo -e "$SUBJ rh.white.H already exists." # check
    fi

    # Replace Right White.K symbolic link with file it points to
    if [ ! -f "$SubFreeSurferDir/symlinks/rh.white.K" ]; then
        mv "$SubSurfDir/rh.white.K" "$SubFreeSurferDir/symlinks"
        cp "$SubSurfDir/rh.white.preaparc.K" "$SubFreeSurferDir"
        mv "$SubFreeSurferDir/rh.white.preaparc.K" "$SubSurfDir/rh.white.K"
    else
        echo -e "$SUBJ rh.white.K already exists." # check
    fi

    # Make temporary copies of FreeSurfer subdirs in main subject dir
    if [ ! -d "$SUBJECTS_DIR"/"$SUBJ"/"$SUBJ" ]; then
        cp -rf "$SubFreeSurferDir" "$SUBJECTS_DIR"/"$SUBJ"
    fi

    # Move files into main subject dir and delete extra dir
    if [ -d "$SUBJECTS_DIR"/"$SUBJ"/"$SUBJ" ]; then
        mv "$SUBJECTS_DIR"/"$SUBJ"/"$SUBJ"/* "$SUBJECTS_DIR"/"$SUBJ" 
        rm -r "$SUBJECTS_DIR"/"$SUBJ"/"$SUBJ"
    fi

done

echo "    ---------------------    Done    ---------------------    "
