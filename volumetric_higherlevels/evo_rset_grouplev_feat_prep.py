# %%
import glob
from my_imaging_tools import fmri_tools

datadir = '/Volumes/EVO_Estia/EVO_MRI/organized/UW'
q = fmri_tools(datadir)

# Make /reg dir in all lower-level Feat dirs (needed for Feat group level)
cmd = [None]*2
dirs = glob.glob('/Volumes/EVO_Estia/EVO_MRI/organized/UW/*/func/rest/rois/*/rest_lowerlev_vol/*.feat')
for dir in dirs:
    cmd[0] = f'mkdir {dir}/reg' # create /reg dir
    cmd[1] = f'cp {dir}/mean_func.nii.gz {dir}/reg' # move mean_func into new dir

    q.exec_cmds(cmd)

# %% Copy identity matrix into new /reg dirs
# NOTE: ident.mat should be in $FSLDIR/etc/flirtsch/ident.mat, wherever that is on your machine
cmd = [None]
dirs = glob.glob('/Volumes/EVO_Estia/EVO_MRI/organized/NKI/*/func/rest/rois/*/rest_lowerlev_vol/*.feat/reg')
for dir in dirs:
    cmd[0] = f'cp /Users/amd_ras/fsl/etc/flirtsch/ident.mat /{dir}/example_func2standard.mat'
    q.exec_cmds(cmd)

# %%
