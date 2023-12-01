# Get text file lists of subjects to exclude from analyses

# Holland Brown

# Updated 2023-12-01
# Created 2023-12-01

# %%
from my_imaging_tools import fmri_tools

maindatadir = f'/Volumes/EVO_Estia/EVO_MRI/organized/'
rest_list_out = f''
task_list_out = f''

bad_anatomical = [''] # list subjects to exclude because of bad anatomical scans
sites = ['NKI','UW']
sessions = ['1','2']
task_runs = ['1','2']
rest_runs = ['1']

# %%
rl = open(f'{rest_list_out}','w')
tl = open(f'{task_list_out}','w')
for site in sites:
    datadir = f'{maindatadir}/{site}'
    q = fmri_tools(datadir) # get subject list and initialize functions

    for sub in q.subs:
        subdir = f'{datadir}/{sub}/func'

        # check if subject is in bad_anatomical list
        if sub in bad_anatomical:
            rl.write(f'{sub}\n')
            tl.close()

        # check subject has data for both sessions

rl.close()
tl.close()