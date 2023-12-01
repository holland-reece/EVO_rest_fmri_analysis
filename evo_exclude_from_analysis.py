# Get text file lists of subjects to exclude from analyses

# Holland Brown

# Updated 2023-12-01
# Created 2023-12-01

# EVO manually exclude:
    # W159 MEP anatomical preproc did not complete (not sure why)
    # 97018 flagged for bad anatomical scan in both Feat & MEP preproc QA -> exclude from all analyses
    # 97035 flagged for significant focal atrophy -> exclude from all analyses
    # 97024 Rest_S2 only has 27 volumes -> exclude from RS higher levels
    # 97025 Rest_S1 not obtained -> exclude from RS higher levels

# %%
import os
from my_imaging_tools import fmri_tools

maindatadir = f'/Volumes/EVO_Estia/EVO_MRI/organized/'
rest_lowerlev_list_out = f'/Users/holland_brown_ra/Desktop/evo_exclude_rest_lowerlev.txt'
rest_higherlev_list_out = f'/Users/holland_brown_ra/Desktop/evo_exclude_rest_higherlev.txt'
task_lowerlev_list_out = f'/Users/holland_brown_ra/Desktop/evo_exclude_task_lowerlev.txt'
task_higherlev_list_out = f'/Users/holland_brown_ra/Desktop/evo_exclude_task_higherlev.txt'

# Manually set subjects to be excluded bc of bad anatomical scans or incomplete data
bad_anatomical = ['97018','97035','97038','W159'] # exclude from both higher and lower levels because of bad anatomical scans
rest_incomplete = ['97024_2','97025_1'] # exclude from resting-state higher levels bc of incomplete data
task_incomplete = [''] # exclude from task-based higher levels bc of incomplete data

sites = ['NKI','UW']
sessions = ['1','2']
task_runs = ['1','2']
rest_runs = ['1']
tasks = ['adjective','floop']

# %% Create list of subjects to exclude based on motion QA

# %% Create text file with list of subjects to exclude from rest analyses
r_low = open(f'{rest_lowerlev_list_out}','w')
r_high = open(f'{rest_higherlev_list_out}','w')
for site in sites:
    datadir = f'{maindatadir}/{site}'
    q = fmri_tools(datadir) # get subject list and initialize functions

    for sub in q.subs:
        subdir = f'{datadir}/{sub}/func'

        # if subject has bad anatomical, exclude from both higher and lower levels
        if sub in bad_anatomical:
            for session in sessions:
                for run in rest_runs:
                    r_low.write(f'{sub}_S{session}_R{run}\n')
            r_high.write(f'{sub}\n')
            continue

        # if subject has incomplete data, exclude subject from higher levels and exclude incomplete session from lower levels
        if sub in rest_incomplete:
            r_high.write(f'{sub}\n')
            for subject in rest_incomplete:
                if sub in subject:
                    r_low.write(f'{subject}\n')
            continue

        # if subject is missing data, exclude subject from higher levels and exclude missing session from lower levels
        counter = 0
        for session in sessions:
            for run in rest_runs:
                run_dir = f'{subdir}/unprocessed/rest/session_{session}/run_{run}'
                if os.path.isdir(run_dir)==False:
                    r_low.write(f'{sub}_S{session}_R{run}\n')
                    counter += 1
        if counter != 0:
            r_high.write(f'{sub}\n')

r_low.close()
r_high.close()

# %% Create text file with list of subjects to exclude from rest analyses
t_low = open(f'{task_lowerlev_list_out}','w')
t_high = open(f'{task_higherlev_list_out}','w')
for site in sites:
    datadir = f'{maindatadir}/{site}'
    q = fmri_tools(datadir) # get subject list and initialize functions

    for sub in q.subs:
        for task in tasks:
            subdir = f'{datadir}/{sub}/func/unprocessed/task/{task}'

            # if subject has bad anatomical, exclude from both higher and lower levels
            if sub in bad_anatomical:
                for session in sessions:
                    for run in task_runs:
                        t_low.write(f'{sub}_{task}_S{session}_R{run}\n')
                t_high.write(f'{sub}_{task}\n')
                continue

            # if subject has incomplete data, exclude subject from higher levels and exclude incomplete session from lower levels
            if sub in task_incomplete:
                t_high.write(f'{sub}_{task}\n')
                for subject in task_incomplete:
                    if sub in subject:
                        t_low.write(f'{subject}\n')
                continue

        # if subject is missing data, exclude subject from higher levels and exclude missing session from lower levels
        counter = 0
        for session in sessions:
            for run in task_runs:
                run_dir = f'{subdir}/unprocessed/task/{task}/session_{session}/run_{run}'
                if os.path.isdir(run_dir)==False:
                    t_low.write(f'{sub}_{task}_S{session}_R{run}\n')
                    counter += 1
        if counter != 0:
            t_high.write(f'{sub}_{task}\n')

t_low.close()
t_high.close()

# %%
