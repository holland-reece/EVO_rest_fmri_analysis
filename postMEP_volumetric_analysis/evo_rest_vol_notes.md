EVO resting-state volumetric lower level scripts: instructions and explanations

Holland Brown

Updated 2023-01-11
Created 2023-01-11

# 1. Run 'create_vol_parc_prep.sh' to move relevant files into main subject directories and delete softlinks before running the volumetric parcellation scripts

### a. Before running this script...

-  Need a copy of this script in the main data directory, where all the subject directories are
- Need a copy of the freesurfer folder in the main data directory (copy this from wherever freesurfer is installed on your machine, or the FreeSurfer repository: https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall)
- Need a list of subject IDs in a text file, separated by newlines (should be whatever the subject directories are named, for example 97023 or W016)
- When you are ready to execute, cd to the main data dir in a shell and change the permissions of the script so you can run it (always need to do this before running any script on the cluster or you will get a permissions error)
    >> chmod +x ./create_vol_parc_prep.sh

### b. After running, you should see...
- all the directories and files from your subjects' freesurfer outputs (/anat/T1w/SUBJECT/*) from running the anatomical ME pipeline into the main subject dir (just need them to run the main voluemtric parcellation script, then they'll be deleted with the cleanup script)
- creates a new dir in the subjects' freesurfer outputs (/anat/T1w/SUBJECT/*) from running the anatomical ME pipeline called /symlinks, where copies of the symbolic links are kept; makes copies of the real files in other dirs in that freesurfer dir
    - without this prep script, the symlinks i.e. softlinks make the volumetric parcellation code crash because it can't find the actual freesurfer files

# 2. Run 'create_subj_volume_parcellation.sh' to project Glasser HCP-MMP1 atlas surface parcellation onto each subject's native FreeSurfer volumetric space

### a. Before running this script...

-  Need a copy of this script in the main data directory, where all the subject directories are
- Need a copy of the freesurfer folder in the main data directory (copy this from wherever freesurfer is installed on your machine, or the FreeSurfer repository: https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall)
- Need a list of subject IDs in a text file, separated by newlines (should be whatever the subject directories are named, for example 97023 or W016)
- Need to have already run the prep script from step 1 of this document, so subjects' freesurfer dirs are in the main dir (looks messy, but it's temporary)
- A directory where you want to put all of your results from this script, which will be dirs named after the subject IDs, so it CAN'T BE THE MAIN DATA DIR dir or it may overwrite your actual subject dirs or just not be able to make the results directory and crash
    - for example, /athena/victorialab/scratch/hob4003/study_EVO/EVO_HCP-MMP1_rest_vol_roi_masks
- Run these three commands in your terminal before executing the script to set up FreeSurfer and FSL in your environment
    >> export FREESURFER_HOME="/home/software/apps/freesurfer6/6.0/freesurfer" # cluster path to FreeSurfer
    >> source "${FREESURFER_HOME}/SetUpFreeSurfer.sh"
    >> module load fsl
- When you are ready to execute, cd to the main data dir in a shell and change the permissions of the script so you can run it
    >> chmod +x ./create_subj_volume_parcellation.sh
- Read the comments at the top of this script, and see the note I made with example commands for this script
    - example: ./create_subj_volume_parcellation.sh -L '/athena/victorialab/scratch/hob4003/study_EVO/NKI_MRI_data/EVOsubjects_test.txt' -a 'HCP-MMP1' -d '/athena/victorialab/scratch/hob4003/study_EVO/EVO_rest/EVO_rest_volumetric/HCP-MMP1_fsaverage_masks' -m YES


### b. After running, you should see...
- all the directories and files from your subjects' freesurfer outputs (/anat/T1w/SUBJECT/*) from running the anatomical ME pipeline into the main subject dir (just need them to run the main voluemtric parcellation script, then they'll be deleted with the cleanup script)
- creates a new dir in the subjects' freesurfer outputs (/anat/T1w/SUBJECT/*) from running the anatomical ME pipeline called /symlinks, where copies of the symbolic links are kept; makes copies of the real files in other dirs in that freesurfer dir
    - without this prep script, the symlinks i.e. softlinks make the volumetric parcellation code crash because it can't find the actual freesurfer files
