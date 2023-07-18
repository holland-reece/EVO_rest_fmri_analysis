# Quality control (for EVO resting-state fMRI data)

# Holland Brown

# Updated 2023-05-03
# Created 2023-03-30

# This code...
    # 1. Creates QC directory in main data dir and a QC dir in each sub's ROI dir
    # 2. Converts AFNI brain_corr and TSNR files to NIFTI; copies these files into sub's QC dir
    # 3. Calculates motion measures -> saves as file in subjects' QC dir
    # 4. Calculates ROI/whole-brain measures -> saves as file in subjects' QC dir

# Sources:
    # 6_quality_control.sh (Lindsay Victoria)
    # 7_CalculateMeanFD.sh -> calculates mean framewise displacement (Lindsay Victoria)

# FIX:
    # write function or class for reading files and formatting outputs as lists and strings (line 190)
    # finish writing section to create ROI-specific output CSV

#--------------------------------------------------
# %% Define functions
def exec_cmds(commands): # run commands in system terminal (must be bash terminal, and function input must be list)
    for command in commands:
        subprocess.run(command, shell=True, executable='/bin/bash') # run command in bash shell

def format_readlist(textfile,FloatOptBoole=False,StripOptBoole=False): # textfile: '/path/to/textfile.txt' , FloatOptBoole: True or False (True to convert to float)
    tf = open(textfile,'r')
    x = tf.readlines()
    tf.close()
    if StripOptBoole==True:
        x = [el.strip('\n') for el in x] # remove newline characters from list
        x = [el.strip(' ') for el in x] # remove space characters from list
    if FloatOptBoole==True:
        x = [float(el) for el in x] # convert elements to float
    return x



# Import packages; set directories and paths
import subprocess
import numpy as np
import os
import pandas as pd

# User sets these paths and variables...
operating_system = 1 # Linux (0) or MacOS (1)
preproc_folder = 'rest_afni_results_ICA'
preprocRestdir = 'rest/rest_preproc.feat' # PreprocessedFolderName (without subject number prefix and underscore)
sublist_txt = 'SubList_EVO_rest_v2.txt' # SubjectListTextFileName.txt
subQCfolder = f'QC_rest' # name of QC folder in subject directories
mainQCfolder = 'EVO_QC_rest' # name of main QC folder in data directory
FDinputMask = 'standard_mask.nii.gz' # name of standard mask file in /preprocRestdir/reg/
FDinputNifti = 'fanaticor.nii.gz' # name of main functional nifti file in /preproc_folder/
roiInputNifti = 'remean_gsr_fanat.nii.gz' # name of roi nifti to be analyzed in wholebrain step
mainOutfile = 'evo_rest_qc_MAIN.csv' # MainOutputFile.csv
roiOutfile = 'evo_rest_qc_ROI.csv' # roiOutputFile.csv (will store tsnr and corr vals for each subject, for each ROI)
roi_list = ['R_MFG','L_MFG','R_rACC','L_rACC'] # list of ROIs on which to run QC

# Linux directories
if operating_system == 0:
    datadir = '/media/holland/LACIE-SHARE/EVO_MRI_data' # main data directory
    roidir = f'/media/holland/LACIE-SHARE/EVO_ROIs'

# MacOS directories
elif operating_system == 1:
    datadir = '/Volumes/LACIE-SHARE/EVO_MRI_data' # main data directory
    roidir = f'/Volumes/LACIE-SHARE/EVO_ROIs'

# Automatically set these directories and paths
sublist = f'{datadir}/{sublist_txt}'
mainQCdir = f'{datadir}/{mainQCfolder}'

# User run options (set to 1 to run, 0 to skip)
get_motion_params = 1 # run Step 2a: copy motion params into QC dir
get_temp_signal_to_noise = 1 # run Step 2b: copy temporal-signal-to-noise ratio into QC dir
get_global_corr = 1 # run Step 2c: copy global correlation into QC dir
motion_measures = 1 # run Step 3: calculate mean, stdd, and max displacement of motion params
wholebrain_measures = 1 # run Step 4: whole brain measures
roi_measures = 1 # roi measures

# Read subject list text file into Python list object
subs = format_readlist(sublist,StripOptBoole=True) # read sublist text file into list necessary for all/any subsequent steps
print(f'{len(subs)} Subjects:')
for sub in subs:
    print(f'\t{sub}')

# Initialize main output dataframe
main_measures_ls = ['Temporal SNR','Global Corr','Framewise Displac'] # don't change
roi_measures_ls = ['TSNR','Corr']
empty_ls = [None]*len(subs) # define empty list to be df column

M_out = pd.DataFrame({'Subjects':subs}) # ROI-specific output dataframe
M_out.set_index('Subjects',inplace=True) # set subject IDs column as index
for i in main_measures_ls:
    M_out.insert(len(M_out.columns),f'{i}',empty_ls)

# Initialize ROI output dataframe
R_out = pd.DataFrame({'Subjects':subs}) # ROI-specific output dataframe
R_out.set_index('Subjects',inplace=True) # set subject IDs column as index
for j in roi_measures_ls:
    for i in roi_list:
        R_out.insert(len(R_out.columns),f'{i} {j}',empty_ls)



# %% Create QC folders in main data dir and subject directories
if os.path.exists(mainQCdir)==False:
    cmd_make_qc_dir = f'mkdir {mainQCdir}'
    exec_cmds([cmd_make_qc_dir])

for sub in subs:
    subQCdir = f'{datadir}/{sub}/{subQCfolder}'
    if os.path.exists(subQCdir)==False:
        cmd_make_sub_qc_dir = f'mkdir {subQCdir}' # create directory for QC outputs in each sub's roi dir
        exec_cmds([cmd_make_sub_qc_dir])



# Get all necessary files from preprocessed dirs
for sub in subs:
    subQCdir = f'{datadir}/{sub}/{subQCfolder}' # subject's roi data directory
    preproc_dir = f'{datadir}/{sub}/{sub}_{preproc_folder}'
    if get_motion_params == 1: # Step 1a: get motion parameters and their derivatives
        if os.path.exists(f'{subQCdir}/motion_timeseries.txt')==False:
            print(f'Copying motion parameters into {sub} QC dir...')
            cmd_copy_motion_params = f'cp {preproc_dir}/motion_demean.1D {subQCdir}/motion_timeseries.txt'
            exec_cmds([cmd_copy_motion_params])

    if get_temp_signal_to_noise == 1: # Get temporal signal-to-noise ratio file
        if os.path.exists(f'{subQCdir}/TSNR.{sub}.nii.gz')==False:
            print(f'Converting AFNI TSNR file to NIfTI for {sub}...')
            cmd_tsnr = f'3dAFNItoNIFTI -prefix {subQCdir}/TSNR.{sub}.nii.gz {preproc_dir}/TSNR.{sub}+tlrc' # 3dAFNItoNIFTI -prefix /path/[output_filename] /path/[input_filename]
            exec_cmds([cmd_tsnr])
    
    if get_global_corr == 1: # Get global correlation file
        if os.path.exists(f'{subQCdir}/corr_brain.nii.gz')==False:
            print(f'Converting AFNI corr_brain file to NIfTI for {sub}...')
            cmd_corrbrain = f'3dAFNItoNIFTI -prefix {subQCdir}/corr_brain.nii.gz {preproc_dir}/corr_brain+tlrc'
            cmd_copy_glob_corr = f'cp {preproc_dir}/out.gcor.1D {subQCdir}/GCOR.txt'
            exec_cmds([cmd_corrbrain,cmd_copy_glob_corr])
        glist = format_readlist(f'{subQCdir}/GCOR.txt',FloatOptBoole=True,StripOptBoole=True) # remove whitespace chars and convert elements to float 
        M_out.loc[f'{sub}','Global Corr'] = glist[0] # global correlation for one subject
print("Done.")



# %% Calculate motion measures -> mean, stdd, and max displacement of motion params, framewise displacement
if motion_measures == 1:
    # Create empty QC files in main QC dir
    mainQCtfs = ['MP_means.txt','MP_stdds.txt','MP_maxdisplac.txt','FD_means.txt']
    for i in mainQCtfs:
        # if os.path.exists(f'{mainQCdir}/{i}')==False:
        cmd_create_QC_file = f'touch {mainQCdir}/{i}'
        exec_cmds([cmd_create_QC_file])

    # Open QC files in write mode
    p = open(f'{mainQCdir}/MP_means.txt','w')
    s = open(f'{mainQCdir}/MP_stdds.txt','w')
    m = open(f'{mainQCdir}/MP_maxdisplac.txt','w')
    f = open(f'{mainQCdir}/FD_means.txt','w')
    
    for sub in subs:
        subQCdir = f'{datadir}/{sub}/{subQCfolder}' # subject's roi QC data directory
        MPs = np.loadtxt(f'{subQCdir}/motion_timeseries.txt',dtype=float) # read motion time series into a numpy array

        # Mean time series for each motion parameter -> get 6 (or number of motion params) values
        m_ts = np.mean(MPs, axis=0) # mean motion parameter time series as numpy array
        np.savetxt(f'{subQCdir}/MP_means.txt',m_ts) # save mean MP time series array as txt file in subj QC dir
        mts_string = f'{sub}' # format m_ts as a string
        for i in range(m_ts.shape[0]): # iterate through elements in m_ts as a 1D array
            mts_string = f'{mts_string}\t{m_ts[i]}' # concatenate strings so each subj has a row of mean motion params
        p.write(f'{mts_string}\n') # write the subject's row on the end of the MP means document

        # Standard deviation of each motion parameter -> get 6 (or number of motion params) values
        stdd_arr = np.std(MPs,axis=0) # calculate standard deviation of each MP time series
        np.savetxt(f'{subQCdir}/MP_stdds.txt',stdd_arr)
        stdd_string = f'{sub}'
        for i in range(stdd_arr.shape[0]):
            stdd_string = f'{stdd_string}\t{stdd_arr[i]}'
        s.write(f'{stdd_string}\n')

        # Maximum displacement for each motion parameter -> get 6 (or number of motion params) values
        max_arr = np.amax(MPs,axis=0) # return max value from each mp time series
        max_string = f'{sub}'
        for i in range(max_arr.shape[0]):
            max_string = f'{max_string}\t{max_arr[i]}'
        m.write(f'{max_string}\n')

        # Mean framewise displacement -> get one mean FD value for each participant
        if os.path.exists(f'{subQCdir}/FD.txt')==False:
            print(f'Calculating framewise displacement for subject {sub}...') # outputs: FD.txt, FD.png
            cmd_motion_outliers = f"fsl_motion_outliers -i {datadir}/{sub}/{sub}_{preproc_folder}/{sub}_{FDinputNifti} -m {datadir}/{sub}/{preprocRestdir}/reg/{FDinputMask} --fd -s {subQCdir}/FD.txt -p {subQCdir}/FD.png -o tmp"
            cmd_motion_outliers2 = f'rm tmp' # remove temporary file
            exec_cmds([cmd_motion_outliers, cmd_motion_outliers2])
        fd = np.loadtxt(f'{subQCdir}/FD.txt') # read framewise displacement file into numpy array
        mean_fd = np.mean(fd, axis=0) # calculate mean column-wise -> outputs 1 value
        f.write(f'{sub}\t{float(mean_fd)}\n')
        M_out.loc[f'{sub}','Framewise Displac'] = float(mean_fd)
    p.close()
    s.close()
    m.close()
    f.close()
    print("Done.")



# Whole-brain
if wholebrain_measures == 1:
    cmd = ['','','','','','']
    for sub in subs:
        subQCdir = f'{datadir}/{sub}/{subQCfolder}' # subject's roi QC data directory

        # Whole-brain TSNR >> subject QC dir
        if os.path.exists(f'{subQCdir}/TSNR_wholebrain.txt')==False:
            print(f'Calculating whole-brain TSNR for subject {sub}...')
            cmd[0] = f'fslstats {subQCdir}/TSNR.{sub}.nii -M > {subQCdir}/TSNR_wholebrain.txt'
            exec_cmds([cmd[0]])

        # Whole-brain TSNR >> main QC dir
        cmd1a = "awk -F' ' '{print $1}' " # had to split this up and recombine bc of brackets syntax
        cmd1b = f'{subQCdir}/TSNR_wholebrain.txt >> {mainQCdir}/TSNR_wholebrain.txt'
        cmd[1] = f'{cmd1a} {cmd1b}' # concatenate commands together
        exec_cmds([cmd[1]])

        # Whole-brain TSNR >> main QC df
        wb_tsnr = format_readlist(f'{subQCdir}/TSNR_wholebrain.txt',FloatOptBoole=True,StripOptBoole=True)
        M_out.loc[f'{sub}',f'Temporal SNR'] = wb_tsnr[0] # save subject's whole-brain tsnr in roi df
    print("Done.")



# ROI-specific measures
if roi_measures == 1:
    for sub in subs:
        subQCdir = f'{datadir}/{sub}/{subQCfolder}' # subject's roi QC data directory
        for roi in roi_list:
            roi_dir = f'{roidir}/{roi}'

            # ROI TSNR >> subject QC dir
            if os.path.exists(f'{subQCdir}/{roi}_TSNR.txt')==False:
                print(f'Calculating {roi} TSNR for subject {sub}...')
                cmd[2] = f"3dROIstats -mask {roi_dir}/{roi}.nii.gz {subQCdir}/TSNR.{sub}.nii.gz | awk 'FNR==2' | cut -f3- > {subQCdir}/{roi}_TSNR.txt"
                exec_cmds([cmd[2]])

            # ROI TSNR >> main QC dir
            cmd3a = "awk -F' ' '{print $1}' " # had to split this up and recombine bc of brackets syntax
            cmd3b = f'{subQCdir}/{roi}_TSNR.txt >> {mainQCdir}/{roi}_TSNR.txt'
            cmd[3] = f'{cmd3a} {cmd3b}' # concatenate commands together
            exec_cmds([cmd[3]])

            # ROI TSNR >> ROI QC df
            rt = format_readlist(f'{subQCdir}/{roi}_TSNR.txt',FloatOptBoole=True,StripOptBoole=True)
            R_out.loc[f'{sub}',f'{roi} TSNR'] = rt[0] # save subject's whole-brain tsnr in roi df

            # ROI Correlation >> subject QC dir
            if os.path.exists(f'{subQCdir}/{roi}_corr.txt')==False:
                cmd[4] = f"3dROIstats -mask {roi_dir}/{roi}.nii.gz {subQCdir}/corr_brain.nii.gz | awk 'FNR==2' | cut -f3- > {subQCdir}/{roi}_corr.txt" # grid of global correlation (GCOR) for ROI
                exec_cmds([cmd[4]])

            # ROI Correlation >> main QC dir
            cmd5a = "awk -F' ' '{print $1}' " # had to split this up and recombine bc of brackets syntax
            cmd5b = f'{subQCdir}/{roi}_corr.txt >> {mainQCdir}/{roi}_corr.txt'
            cmd[5] = f'{cmd5a} {cmd5b}' # concatenate commands together
            exec_cmds([cmd[5]])

            # ROI Corr >> ROI QC df
            rc = format_readlist(f'{subQCdir}/{roi}_corr.txt',FloatOptBoole=True,StripOptBoole=True)
            R_out.loc[f'{sub}',f'{roi} Corr'] = rc[0] # save subject's whole-brain tsnr in roi df
    print("Done.")



#  Save roi and main QC dataframes as CSV files
M_out.to_csv(f'{mainQCdir}/{mainOutfile}')
R_out.to_csv(f'{mainQCdir}/{roiOutfile}')

# %%
# for sub in subs:
#     olddir = f'{datadir}/{sub}/quality_control'
#     newdir = f'{datadir}/{sub}/{subQCfolder}'
#     c = f'mv {olddir}/FD.png {newdir}'
#     exec_cmds([c])


# dirs2remove = [f'{subQCfolder}']
# files2remove = ['']

# for sub in subs:
#     # Remove subject directories
#     for featDir in dirs2remove:
#         subDir = f'{datadir}/{sub}/{featDir}'
#         if os.path.exists(subDir):
#             print(f'{featDir}  :  {sub}')
#             cmd_rmDir = f'rm -r {subDir}'
#             exec_cmds([cmd_rmDir])

    # # Remove files from subject directories
    # for f in files2remove:
    #     fDir = f'{datadir}/{sub}/{subQCfolder}/{f}'
    #     if os.path.exists(fDir):
    #         print(f'{f}  :  {sub}')
    #         cmd_rmFile = f'rm {fDir}'
    #         exec_cmds([cmd_rmFile])

# Remove main QC dir
# maindir = f'{datadir}/EVO_quality_control'
# if os.path.exists(mainQCdir):
#     cmd_rmMain = f'rm -r {mainQCdir}'
#     exec_cmds([cmd_rmMain])

# # Remove files from main QC dir
# mainQCfiles = ['FD_means.csv','MP_maxdisplac.csv','MP_means.csv','MP_stdds.csv'] # files to remove from main QC dir
# for m in mainQCfiles:
#     mpath = f'{mainQCdir}/{m}'
#     if os.path.exists(mpath):
#         cmd_rm = f'rm {mpath}'
#         exec_cmds([cmd_rm])