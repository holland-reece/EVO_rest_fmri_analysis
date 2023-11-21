# Brain Extraction with FSL BET: use this script to get masks for fieldmap preprocessing

# Holland Brown

# Updated 2023-06-23
# Created 2023-06-08

# This script...
    # runs brain extraction for anatomical images using FSL BET
    # used in EVO study to create masks for ICA-AROMA denoising and fieldmap preprocessing

# References:
    # FSL BET User Guide: https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/BET/UserGuide
    # MumfordBrainStats Brain Extraction: https://www.youtube.com/watch?v=xxSEx2NTM-w
    # ICA-AROMA Manual.pdf >> "Masking"
    
# -------------------------------------------------------------------------------------------------------------------
# %% Set up
def read_txtlist(txtlist):
    t = open(txtlist,'r') # open subject list text file in read mode
    tlist = t.readlines() # create list of string objects
    t.close() # close text file
    tlist = [el.strip('\n') for el in tlist] # remove newline characters from list
    tlist = [el.strip(' ') for el in tlist] # remove space characters from list
    tlist = [el.strip('\t') for el in tlist]
    return tlist

def exec_cmds(commands): # run commands in system terminal (must be bash terminal, and function input must be list)
    for command in commands:
        subprocess.run(command, shell=True, executable='/bin/bash') # run command in bash shell

import subprocess


datadir = '/media/holland/LACIE-SHARE/EVO_MRI_data' # main data directory
sublist = f'/home/holland/Desktop/subs2run_bet.txt'

# subs=['97035_1']
subs = read_txtlist(sublist)
print('Subjects:')
for sub in subs:
    print(sub)

# BETopts = '-n -f 0.3 -m -R' # space-separated list of BET options inside one string
BETopts = '-n -f 0.3 -m -B' # these options work best for anat skull-strip

# %% Skull-strip example func data to create ICA-AROMA mask
cmd=['','']
for sub in subs:
    print(f'Running BET for subject {sub}...')
    indir = f'{datadir}/{sub}/rest_preproc.feat'
    outdir = f'{datadir}/{sub}/rest_preproc.feat'
    cmd[0] = f'bet {indir}/example_func {outdir}/icaaroma_example_func {BETopts}'
    exec_cmds([cmd[0]])
print("\nDone.")

# %% Skull-strip anatomicals
cmd=['']
for sub in subs:
    print(f'Running BET for subject {sub}...')
    indir = f'{datadir}/{sub}/anat'
    outdir = f'{datadir}/{sub}/anat'
    cmd[0] = f'bet {indir}/anat {outdir}/anat_brain {BETopts}'
    exec_cmds(cmd)
print("\nDone.")
# %%
