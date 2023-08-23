# EVO Lower-level ROI analysis

# Holland Brown

# Updated 2023-08-23
# Created 2023-03-20

# Notes:
    # is it ok that dims and pixdims (in nifti headers) don't match protocols? >> https://github.com/nipreps/fmriprep/issues/2315
    # for multiple comparisons correction using fdr, see source >> https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FDR
    # so far, fdr has only returned 0; found online that it doesn't use spatial signal, so may not pick up anything >> https://www.jiscmail.ac.uk/cgi-bin/webadmin?A2=FSL;82415e6.0807

# Fix:
    # add bifurcating selection statements in Step 5 to accomodate different TRs between sites (for now, run WCM and UW ppts separately)

# Recent changes:
    # 2023-05-18: expanded read subject list section to automatically adjust for only running 1 site's ppts and change TR accordingly
    # 2023-04-21: added statement in remean block to delete previous gsr nifti file if both remean & gsr are run (final nifti input is both gsr & remean)
    # 2023-04-18: removed try/except statements (may have been interfering w/ handoff between code body and functions, or silencing error messages)


#---------------------------------------------------------------------------------------------------------------
# %% Define functions
def read_sublist(subjlist):
    s = open(subjlist,'r') # open subject list text file in read mode
    subjs = s.readlines() # create list of string objects
    s.close() # close text file
    subjs = [el.strip('\n') for el in subjs] # remove newline characters from list
    subjs = [el.strip(' ') for el in subjs] # remove space characters from list
    subjs = [el.strip('\t') for el in subjs]
    return subjs

def exec_cmds(commands): # run commands in system terminal (must be bash terminal, and function input must be list)
    for command in commands:
        subprocess.run(command, shell=True, executable='/bin/bash') # run command in bash shell




# Setup 1: import modules; set directories, paths, and user run options
import subprocess
import os


operating_system = 0 # Linux (0) or MacOS (1)
roi = 'L_MFG' # name of ROI mask, will be used to create directories and Feat design file
feat_fn = 'evo_lower_level.fsf' # FeatFileName.fsf
# feat_outdir = 'lower_level_remean.feat' # name of the output directory
sublist_tf = f'{roi}_subs2run.txt' # SubjectListName.txt
preproc_folder = 'rest_ICA_AROMA' # PreprocessedInputsFolder -> omit subject ID from beginning, will look like dir/<subjectID>_PreprocessedInputsFolder
# afni_fn = '' # AfniFileName+tlrc -> fn of .HEAD and .BRIK afni files, omit subject ID
afni_fn1 = 'errts.' # first half of afni fn (had to do this bc subj ID is in the middle)
afni_fn2 = '.fanaticor+tlrc' # second half of afni fn (had to do this bc subj ID is in the middle)
nifti_fn = 'denoised_func_data_nonaggr.nii.gz' # NiftiInputFileName.nii.gz -> fn after AFNI-NIFTI conversion, will be <subjectID>_NiftiInputFileName.nii.gz
nifti_gsr_fn = 'NotRunning' # name of nifti file after global signal regression (NOT RUNNING FOR EVO)
nifti_remean_fn = 'denois_func_nonaggr_remean.nii.gz'
roi_tn = 'remean2.txt' # leave out roi name and underscore -> will be concatenated w roi name, so you can just make it '.txt'
timestep_WCM_site = 1.4 # TR for data collected at WCM
timestep_UW_site = 1.399999 # TR for data collected at UW


# LINUX DIRECTORIES
if operating_system == 0:
    datadir = '/media/holland/LACIE-SHARE/EVO_MRI_data' # main data directory
    # sublist = f'/home/holland/Desktop/{sublist_tf}' # full/path/to/subjectlist.txt
    roi_dir = '/media/holland/LACIE-SHARE/EVO_ROIs' # directory where ROI masks are located
    # feat_df = f'/media/holland/LACIE-SHARE/{feat_fn}' # full/path/to/{feat_fn}

    # datadir = '/home/holland/Desktop/temp_datadir' # main data directory
    # sublist = f'/home/holland/Desktop/{sublist_tf}' # full/path/to/subjectlist.txt
    # roi_dir = '/home/holland/Desktop/EVO_ROIs' # directory where ROI masks are located
    feat_df = f'/home/holland/Desktop/{feat_fn}' # full/path/to/{feat_fn}

# MAC DIRECTORIES
elif operating_system == 1:
    datadir = '/Volumes/LACIE-SHARE/EVO_MRI_data' # main data directory
    sublist = f'/Volumes/LACIE-SHARE/EVO_MRI_data/{sublist_tf}' # full/path/to/subjectlist.txt
    roi_dir = '/Volumes/LACIE-SHARE/EVO_ROIs' # directory where ROI masks are located
    feat_df = f'/Volumes/LACIE-SHARE/evo_ana_scripts/{feat_fn}' # full/path/to/{feat_fn}


# Setup 2: User run options (1 to run, 0 to skip)
only_WCM_site = 1
only_UW_site = 0

run_create_roi_dirs = 1 # run Step 4 -> makes an ROI directory in each participant's directory; this is where Feat ana dir, fsf file and txt file will go
run_afni2nifti = 0 # run Step 1 -> converts AFNI .HEAD and .BRIK files into one nifti file
run_global_signal_regression = 0 # run Step 1b (if gsr was not included in preprocessing and data needs it)
run_remean = 1 # run Step 2 (only if necessary) -> see notes on WMECC and EVO studies
run_extract_timeseries = 1 # run Step 3 -> takes nifti data file and nifti mask file, returns roi text file for lower level Feat input
run_lower_level_ana = 1 # run Step 5 -> lower level Feat analysis


# %% Read subject list text file; if only running one site, filter out subs from other site and set timestep
# subs = read_sublist(sublist) # read sublist text file into list necessary for all/any subsequent steps
# subs=['97032_1','97032_2','97035_1','97035_2']
subs=['97032_1']
print(f'{len(subs)} subjects.')
listcopy=[]
i=0

if only_WCM_site==1:
    timestep=timestep_WCM_site
    for i in range(len(subs)):
        s=subs[i]
        if s[0]!='W': # remove UW ppts to only run WCM
            listcopy.append(s)
        i+=1

if only_UW_site==1:
    listcopy2=listcopy # duplicate of subs for iteration (subs will change size)
    timestep=timestep_UW_site
    i=0
    for i in range(len(subs)):
        s=subs[i]
        if s[0]=='W': # remove UW ppts to only run WCM
            listcopy2.append(s)
        i+=1

if only_WCM_site==1:
    subs=listcopy
if only_UW_site==1:
    subs=listcopy2
    
for sub in subs:
    print(sub)
print(f'Number of subjects: {len(subs)}')
print(f'Timestep: {timestep}')



# %%
# 1. Create ROI dirs in every ppt's dir (ref: MkDir_ROI)
if run_create_roi_dirs == 1:
    numdirsCreated = 0 # counter -> number of directories created
    cmd_list = [''] # define bash commands
    for sub in subs:
        new_dir = f'{datadir}/{sub}/{roi}'
        dir_exists = os.path.exists(new_dir)
        if dir_exists == False:
            numdirsCreated += 1
            cmd_list[0] = f'mkdir {datadir}/{sub}/{roi}' # create ROI dir in subj dir
            exec_cmds(cmd_list) # execute bash commands in system terminal
        else:
            print(f'ROI directory already exists for {sub}.\n')
    print(f'{numdirsCreated} ROI directories created.\n\n')


# 2. Convert preprocessed AFNI files into NIFTI files
if run_afni2nifti == 1:
    numfilesConverted = 0 # counter -> number of participants for whom AFNI files were converted
    cmd_list = [''] # reserve memory for commands
    for sub in subs:
        # preproc_dir = f'{datadir}/{sub}/{sub}_{preproc_folder}' # subject's preprocessed data directory
        preproc_dir = f'{datadir}/{sub}'
        alreadyNifti = os.path.exists(f'{preproc_dir}/{sub}_{nifti_fn}') # check if NIfTI file is already there
        if alreadyNifti==False: # if NIfTI file isn't there, convert AFNI to NIfTI...
            if os.path.exists(f'{preproc_dir}/{afni_fn1}{sub}{afni_fn2}')==True:
                numfilesConverted += 1
                print(f'Converting AFNI to NIFTI files for {sub}...\n')
                cmd_list[0] = f'3dAFNItoNIFTI -prefix {preproc_dir}/{sub}_{nifti_fn} {preproc_dir}/{afni_fn1}{sub}{afni_fn2}' # AFNI cmd syntax: '3dAFNItoNIFTI [output_filename] [input_filename]'
                exec_cmds(cmd_list) # execute bash commands in system terminal
            else:
                print(f'No AFNI file for subject {sub}.\n')
        elif alreadyNifti==True:
            print(f'{sub} nifti already exists...')
    print(f"{numfilesConverted} subjects' AFNI files converted to NIFTI (of {len(subs)} subjects).\n\n")


# 3. Global Signal Regression -> "regress out" global time series
if run_global_signal_regression == 1:
    numGSR = 0 # counter -> number of subjects for whom gsr nifti files were created
    cmd_list1 = [''] # reserve memory for first set of commands -> extract global time series (have 2 comd execution steps so I can create design matrix using Python in the middle)
    cmd_list2 = ['','',''] # reserve memory for second set of commands -> create general linear model (GLM) of preproc nifti using global time series as regressor, return gsr nifti, clean up files
    for sub in subs:
            # NOTE: found below cmd for "demeaning" in fslmaths cmdline docs - may want to test this out at some point
            # cmd_remean = f'fslmaths {preproc_dir}/{sub}_{nifti_fn} -Tmean -mul -1 -add {preproc_dir}/{sub}_{nifti_fn} {preproc_dir}/{sub}_{nifti_remean_fn}'

        preproc_dir = f'{datadir}/{sub}/{sub}_{preproc_folder}'
        # preproc_dir = f'{datadir}/{sub}'
        input_nifti = f'{preproc_dir}/{sub}_{nifti_fn}'
        output_nifti = f'{preproc_dir}/{sub}_{nifti_gsr_fn}'
        gsrNiftiAlready = os.path.exists(f'{output_nifti}') # check if gsr nifti already exists
        if gsrNiftiAlready == False: # if there is not yet a gsr nifti file for this participant...
            numGSR += 1
            print(f'Extracting global time series for subject {sub}...\n')
            cmd_list1[0] = f'fslmeants -i {input_nifti} -o global_mean.txt' # extract global time series from preprocessed nifti file
            exec_cmds(cmd_list1)

            # Create design_matrix.txt
            gm = open('global_mean.txt','r')
            globm = gm.readlines()
            gm.close()
            dm = open('design_matrix.txt','w')
            for i in range(len(globm)):
                if i != len(globm):
                    globm[i] = globm[i].strip('\n')
                    globm[i] = globm[i].strip(' ')
                    dm.write(f'{globm[i]}\t1\n') # delimeter is tab
                elif i == len(globm):
                    globm[i] = globm[i].strip('\n')
                    globm[i] = globm[i].strip(' ')
                    dm.write(f'{globm[i]}\t1') # delimeter is tab
            dm.close()

            print(f'LinReg model of preprocessed nifti for subject {sub}...\n') # perform linear regression using global mean as a regressor
            cmd_list2[0] = f'fsl_glm -i {input_nifti} -d design_matrix.txt --out_res=residuals.nii.gz' # GLM of preproc nifti (option to demean the data with fnctn opt "-demean")
            cmd_list2[1] = f'cp residuals.nii.gz {output_nifti}' # copy residuals into preproc dir and rename
            cmd_list2[2] = f'rm global_mean.txt design_matrix.txt residuals.nii.gz' # remove temporary files
            exec_cmds(cmd_list2)
        else:
            print(f'GSR NIfTI already exists for {sub}.\n')
    print(f"Global signal regression done for {numGSR} of {len(subs)} subjects.")
    nifti_fn = nifti_gsr_fn # rename main nifti input file to be the gsr nifti file
    print(f'NIfTI input file is now "{nifti_fn}".\n\n')


# 4. Re-mean (do this if activation maps are total null; fsl expects data to be centered at 10,000)
# adds 10,000 to EPI file before time series extraction to shift mean (time-series extraction takes mean activation of roi)
if run_remean == 1:
    for sub in subs:
        preproc_dir = f'{datadir}/{sub}/{sub}_{preproc_folder}'
        # preproc_dir = f'{datadir}/{sub}'
        remeanExists = os.path.exists(f'{preproc_dir}/{sub}_{nifti_remean_fn}')
        if remeanExists == False:
            print(f'Translating global mean by 10,000 for {sub}...\n')
            cmd_remean = f'fslmaths {preproc_dir}/{sub}_{nifti_fn} -add 10000 {preproc_dir}/{sub}_{nifti_remean_fn}'
            exec_cmds([cmd_remean])
        else:
            print(f'Remeaned NIfTI file already exists for subject {sub}...\n')

        if run_global_signal_regression == 1: # if running both remean and gsr, remove prev gsr nifti files
            gsrFileExists = os.path.exists(f'{preproc_dir}/{sub}_{nifti_gsr_fn}')
            if gsrFileExists == True: # if gsr nifti exists, remove it
                cmd_rm_duplicate_nifti = f'rm {preproc_dir}/{sub}_{nifti_gsr_fn}'
                exec_cmds([cmd_rm_duplicate_nifti])
            else: # if gsr nifti doesn't exist, print a warning message
                print(f'WARNING: {sub} GSR NIfTI file does not exist and was not used to calculate remeaned NIfTI file.\n')
    print('EPI files remeaned.')
    nifti_fn = nifti_remean_fn # rename main nifti input file to be the remeaned nifti file
    print(f'NIfTI input file is now "{nifti_fn}".\n\n')

    

#%%
# preproc_dir = f'{datadir}/{sub}/{sub}_{preproc_folder}'
# cmd=[f'fslreorient2std {preproc_dir}/{sub}_{nifti_fn} {preproc_dir}/{sub}_denois_nonaggr_remean_std.nii.gz']
# exec_cmds(cmd)
nifti_fn='denois_nonaggr_remean_std.nii.gz'

# 5. Extract timeseries from ROIs for input into Level 1 analysis (ref: ROI_timeseries.sh)
# fslmeants -> output avg time series of set of voxels, or indiv time series for each of specified voxels
if run_extract_timeseries == 1:
    numtsExtracted = 0 # counter -> number of subjects for whom ROI time series files were created
    cmd_list = [''] # reserve memory for commands
    for sub in subs:
        # nifti_input = f'{datadir}/{sub}/{sub}_{preproc_folder}/{sub}_{nifti_fn}' # subject's preprocessed AFNI ICA results dir
        nifti_input = f'{datadir}/{sub}/{sub}_{preproc_folder}/{sub}_{nifti_fn}'
        new_roi_path = f'{datadir}/{sub}/{roi}/{roi}_{roi_tn}' # subject's roi analysis dir
        tsAlready = os.path.exists(f'{new_roi_path}') # check if time series file already exists for this participant
        if tsAlready == False: # if time series file doesn't exist...
            numtsExtracted += 1
            print(f'Extracting ROI time series for {sub}...\n')
            cmd_list[0] = f'fslmeants -i {nifti_input} -o {new_roi_path} -m {roi_dir}/{roi}/{roi}.nii.gz' # calculate mean time series; function takes (1) path to input NIfTI, (2) path to output text file, (3) path to mask NIfTI
            exec_cmds(cmd_list) # execute bash commands in system terminal
        else:
            print(f'ROI time series file already exists for subject {sub}...\n')
    print(f'ROI time series extracted for {numtsExtracted} of {len(subs)} subjects.\n\n')

# %%

# 6. Run lower-level analysis using design template (ref: first_level5.sh)
if run_lower_level_ana == 1: # Step 1 commands search and replace terms in design file that are the same for all subjects
    cmd_step1 = ['','','','','']
    if os.path.exists(f'{datadir}/{feat_fn}')==False:
        cmd_step1[0] = f'cp {feat_df} {datadir}' # copy design file into preproc dir
        print(f'Creating generalized Feat design file for all analyses...\n')

        # Linux search-and-replace commands
        if operating_system == 0:
            cmd_step1[1] = f"sed -i 's/ROI/{roi}/g' {datadir}/{feat_fn}" # search-and-replace roi in design file
            cmd_step1[2] = f"sed -i 's/TIMESTEP/{timestep}/g' {datadir}/{feat_fn}" # search-and-replace subject in design file
            cmd_step1[3] = f"sed -i 's/INPUTNIFTI/{nifti_fn}/g' {datadir}/{feat_fn}" # search-and-replace nifti input file name (still have to put correct path into design file before running)
            cmd_step1[4] = f"sed -i 's/REGIONOFINTERESTTXT/{roi_tn}/g' {datadir}/{feat_fn}" # search-and-replace ROI text file name (still have to put correct path into design file before running)

        # MacOS search-and-replace commands
        elif operating_system == 1:
            cmd_step1[1] = f"sed -i '' s/ROI/{roi}/g {datadir}/{feat_fn}" # search-and-replace roi in design file
            cmd_step1[2] = f"sed -i '' s/TIMESTEP/{timestep}/g {datadir}/{feat_fn}" # search-and-replace subject in design file
            cmd_step1[3] = f"sed -i '' s/INPUTNIFTI/{nifti_fn}/g {datadir}/{feat_fn}" # search-and-replace nifti input filename (still have to put correct path into design file before running)
            cmd_step1[4] = f"sed -i '' s/REGIONOFINTERESTTXT/{roi_tn}/g {datadir}/{feat_fn}" # search-and-replace ROI text file name (still have to put correct path into design file before running)
        exec_cmds(cmd_step1) # execute bash commands in system terminal
        print("Done.")

    elif os.path.exists(f'{datadir}/{feat_fn}')==True:
        cmd_step1[0] = ''
        print("Generalized Feat design file already exists in main data directory.")
    


    # duplicate_featdirs = [] # create list to save subject IDs that already had Feat dirs of this name
    for sub in subs: # Step 2 commands search and replace terms that are different for each participant
        full_feat_outdir = f'{datadir}/{sub}/{roi}'
        # if os.path.exists(full_feat_outdir):
            # print(f'WARNING: Feat directory already exists for {sub}...\nDuplicate Feat dir will be created...\n')
            # duplicate_featdirs.append(f'{sub}')

        print(f'Creating Feat design file for subject {sub}...\n')
        cmd_step2 = ['','','']
        outdir = f'{datadir}/{sub}/{roi}'
        cmd_step2[0] = f'cp {datadir}/{feat_fn} {outdir}' # copy design file into preproc dir

        if operating_system == 0: # Linux search-and-replace commands
            cmd_step2[1] = f"sed -i 's/SUBJ/{sub}/g' {outdir}/{feat_fn}" # search-and-replace subject in design file
        elif operating_system == 1: # MacOS search-and-replace commands
            cmd_step2[1] = f"sed -i '' s/SUBJ/{sub}/g {outdir}/{feat_fn}" # search-and-replace roi in design file
        cmd_step2[2] = f'feat {outdir}/{feat_fn}' # run fsf file
        exec_cmds(cmd_step2) # execute bash commands in system terminal
        print(f'Running Feat analysis for {sub}...\n')
    print('Feat analyses done.\n\n')
    # if len(duplicate_featdirs) != 0:
        # print(f'{len(duplicate_featdirs)} duplicate Feat directories were created.\nSubjects with duplicate Feat dirs:\n')
        # for i in range(len(duplicate_featdirs)):
            # print(duplicate_featdirs[i])

# %% Remove or rename files and directories (run as needed)
# dirs2remove = [f'R_MFG/lower_level_remean.feat']
# files2remove = [f'R_MFG/evo_lower_level.fsf']
# i = 0 # counter -> number of directories removed
# j = 0 # counter -> number of files removed
# k = 0 # counter -> number of files or directories renamed

# for sub in subs:
#     # Remove directories
#     for featDir in dirs2remove:
#         subDir = f'{datadir}/{sub}/{featDir}'
#         if os.path.exists(subDir):
#             # i+=1
#             print(f'{featDir}  :  {sub}')
#             cmd_rmDir = f'rm -r {subDir}'
#             exec_cmds([cmd_rmDir])

#     # Remove files
#     for anaFile in files2remove:
#         subFile = f'{datadir}/{sub}/{anaFile}'
#         if os.path.exists(subFile):
#             # j+=1
#             print(f'{anaFile}  :  {sub}')
#             cmd_rmFile = f'rm {subFile}'
#             exec_cmds([cmd_rmFile])

#        # Use this code block (instead of above) if path includes subject ID
#     subFile = f'{datadir}/{sub}/{sub}_{preproc_folder}/{sub}_remeaned_fanat.nii.gz'
#     if os.path.exists(subFile):
#         j+=1
#         cmd_rmFile = f'rm {subFile}'
#         exec_cmds([cmd_rmFile])

#     # Rename directories or files
#     subRename = f'{datadir}/{sub}/{sub}_{preproc_folder}/{sub}_remean_fanat2.nii.gz'
#     newName = f'{datadir}/{sub}/{sub}_{preproc_folder}/{sub}_remean_fanat.nii.gz'
#     if os.path.exists(subRename):
#         k+=1
#         cmd_rename1 = f'rm {newName}' # first remove older duplicate file
#         cmd_rename2 = f'mv {subRename} {newName}' # then rename newer file
#         exec_cmds([cmd_rename1,cmd_rename2])
# print(f'{i} directories removed')
# print(f'{j} files removed')
# print(f'{k} files or directories renamed')