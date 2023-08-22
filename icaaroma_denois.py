# Batch-remove MELODIC Independent Components With ICA-AROMA

# Holland Brown

# Updated 2023-06-21
# Created 2023-06-06

# This script...
    # runs ICA-AROMA automated IC removal on all subjects in subjectlist.txt

# Before running...
    # 1. preprocess your data using FEAT with MELODIC ICA turned on

# References:
    # ICA Tutorial: http://www.newbi4fmri.com/tutorial-10-ica
    # AROMA vs. FIX for automated IC removal: https://www.sciencedirect.com/science/article/pii/S221315821730164X
    # ICA-AROMA GitHub: https://github.com/maartenmennes/ICA-AROMA

# -------------------------------------------------------------------------------------------------------------------
# %% Set up
def exec_cmds(commands): # run commands in system terminal (must be bash terminal, and function input must be list)
    for command in commands:
        subprocess.run(command, shell=True, executable='/bin/bash') # run command in bash shell

def read_txtlist(txtlist):
    t = open(txtlist,'r') # open subject list text file in read mode
    tlist = t.readlines() # create list of string objects
    t.close() # close text file
    tlist = [el.strip('\n') for el in tlist] # remove newline characters from list
    tlist = [el.strip(' ') for el in tlist] # remove space characters from list
    tlist = [el.strip('\t') for el in tlist]
    return tlist



import subprocess
# import os



datadir = '/media/holland/LACIE-SHARE/EVO_MRI_data' # main data directory
# datadir='/home/holland/Desktop'
sublist = '/home/holland/Documents/EVO_py_scripts/evo_rest_preproc2/preproc_subs_TEST_UW.txt' # subject ID list in text file
mask_nifti = 'icaaroma_example_func_mask.nii.gz'
icaaromapydir = '/home/holland/ICA-AROMA-master/ICA_AROMA.py'

subs=['97032_1']
# subs = read_txtlist(sublist)
print("Subjects:")
for sub in subs:
    print(f'\t{sub}')


# %% ICA-AROMA automated IC removal
cmd=['']
for sub in subs:
    feat_dir=f'{datadir}/{sub}/rest_preproc.feat'
    infile = f'{feat_dir}/filtered_func_data.nii.gz'
    outdir = f'/{feat_dir}/{sub}_rest_ICAAROMA_aggr'
    affmat = f'{feat_dir}/reg/example_func2highres.mat'
    warp_nifti = f'{feat_dir}/reg/highres2standard_warp.nii.gz'
    mcpar = f'{feat_dir}/mc/prefiltered_func_data_mcf.par'
    # melodic_dir = f'{feat_dir}/filtered_func_data.ica'
    mask=f'{feat_dir}/{mask_nifti}'


    print(f'\nRunning ICA AROMA for subject {sub}...\n')
    # cmd[0]=f"""python {icaaromapydir} -feat {feat_dir} -out /home/holland/Desktop/{sub}_rest_ICAAROMA -m {mask_dir}"""
    cmd[0] = f' python {icaaromapydir} -i {infile} -o {outdir} -a {affmat} -w {warp_nifti} -mc {mcpar} -m {mask} -den aggr'
    exec_cmds(cmd)

# %% Temporal Filtering (should be after ICA-AROMA)
cmd=['']
for sub in subs:
    feat_dir=f'{datadir}/{sub}/rest_preproc.feat'
    icaaroma_dir=f'{feat_dir}/{sub}_rest_ICAAROMA_aggr'
    infile=f'{icaaroma_dir}/denoised_func_data_aggr.nii.gz'
    outfile=f'{feat_dir}/filtered_func_aggrdenois_bptf.nii.gz'
    cmd[0]=f'fslmaths {infile} -bptf 25.0 -1 {outfile}'
    exec_cmds(cmd)
# %%
