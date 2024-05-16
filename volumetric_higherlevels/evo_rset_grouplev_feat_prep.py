# %%
import glob
from my_imaging_tools import fmri_tools

datadir = '/media/holland/EVO_Estia/EVO_MRI/organized/NKI'
q = fmri_tools(datadir)

# %% Make /reg dir in all lower-level Feat dirs (needed for Feat group level)
cmd = [None]*1
dirs = glob.glob('/media/holland/EVO_Estia/EVO_MRI/organized/NKI/*/func/rest/rois/*/rest_lowerlev_vol/*.feat')
for dir in dirs:
    # cmd[0] = f'mkdir {dir}/reg' # create /reg dir
    # cmd[1] = f'cp {dir}/mean_func.nii.gz {dir}/reg' # move mean_func into new dir
    cmd[0] = f'mv {dir}/reg/mean_func.nii.gz {dir}/reg/standard.nii.gz' # move mean_func into new dir


    q.exec_cmds(cmd)

# %% Copy identity matrix into new /reg dirs
# NOTE: ident.mat should be in $FSLDIR/etc/flirtsch/ident.mat, wherever that is on your machine
cmd = [None]
dirs = glob.glob('/Volumes/EVO_Estia/EVO_MRI/organized/NKI/*/func/rest/rois/*/rest_lowerlev_vol/*.feat/reg')
for dir in dirs:
    cmd[0] = f'cp /Users/amd_ras/fsl/etc/flirtsch/ident.mat /{dir}/example_func2standard.mat'
    q.exec_cmds(cmd)

# %% Run group level Feat models
rois = ['L_MFG','R_MFG','L_rACC','R_rACC','R_dACC']
# datadir = '/media/holland/EVO_Estia/EVO_MRI/organized/NKI'
# q = fmri_tools(datadir)

cmd = [None]
for roi in rois:
    cmd[0] = f'feat /media/holland/EVO_Estia/EVO_rest_higherlev_vol/{roi}_grouplevel.fsf'
    q.exec_cmds(cmd)

# %%
