EVO Resting-state fMRI Analysis

Holland Brown

Updated 2023-05-02
Created 2023-04-27

----------------------------------------------------------------------------------------

# Scripts
    Lower Level Resting-state ROI Analysis >> evo_rest_lower_level.py
    Higher Level Resting-state ROI Analysis >> evo_rest_higher_level.py

# Lower Level Resting-state ROI Analysis
> seed-based correlation analysis for a region of interest
> resting-state functional data
> within-subjects analysis

### This code optionally...
1. Creates ROI directories in every subject's directory (destination for Feat analysis output directories)
2. Converts preprocessed AFNI files into NIFTI files
3. Performs global signal regression
4. 'Re-means' data by adding 10,000 to EPI files, ie. linearly shifts global mean from zero to 10,000
5. Extracts ROI timeseries from NIfTI input files for seed-based correlation analysis
6. Runs lower-level Feat analysis (stats only) using design template (need to create template.fsf file before running)

### Usage
1. Before running, make sure you have...
    - preprocessed AFNI (or NIfTI) resting-state fMRI files
    - FSL installed on your machine, and path to the FSL brain template you want to use, e.g. /Users/holland/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz
    - subject list text file
    - template.fsf file (FSL design file)
        > should have the following 'wildcards' wherever there is subject ID (SUBJ), TR (TIMESTEP), roi (ROI), nifti input filename (INPUTNIFTI), roi time series (REGIONOFINTERESTTXT)
        > in fsf file under "Standard Image" (around line 246), put path and filename of your chosen FSL brain template

2. Set paths to input/output files and directories, timestep (the TR for your data), operating system (MacOS or Linux) and user run options
    - Note: if your data is from multiple sites and each site has a different TR, you have to run these separately -> create separate subject lists
    - Note: every step checks if the output files already exist, and if they do, skips the step for that participant -> will not overwrite files of the same name

3. Run, either...
    1. in a bash terminal (will run everything successively without stopping and you may not see printed status statements), OR...
    2. in a Python compiler, such as VS Code
        > if you use VS Code you can run evo_lower_level.py like a jupyter notebook, so you execute each code block that begins with "# %%" separately
            >> allows you to check the outputs of all previous steps before running the Feat analysis step
    Note: either way, you have to set the environment (called the Interpreter in VS Code) to one that has fsl installed (and jupyter kernel if you want to use that)

# Higher Level Resting-state ROI Analysis
> resting-state functional data
> between-subjects comparison of lower level (ROI seed-based correlation) results
> within-subjects comparison from time 1 (pre-treatment) to time 2 (post-treatment)
> group-level comparison from time 1 (pre-treatment) to time 2 (post-treatment)

