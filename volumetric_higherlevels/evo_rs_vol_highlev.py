# EVO Post-MEP Resting-State Higher-Level Mixed Effects Linear Model Using Python statsmodels

# Holland Brown

# Updated 2024-03-28
# Created 2024-03-20



# %%
import os
import numpy as np
import pandas as pd
import nibabel as nib
import statsmodels.api as sm
import statsmodels.formula.api as smf
from my_imaging_tools import fmri_tools
import csv


def mixed_effects_model(connectivity_data, time_points, treatment_groups):
    """
    Create a mixed-effects linear model for ROI-to-wholebrain functional connectivity.

    Parameters:
    - connectivity_data: DataFrame containing ROI-to-wholebrain functional connectivity data.
                         Each row represents a participant, and columns represent connectivity values.
    - time_points: List or array containing time points (e.g., pre-treatment, post-treatment) for each participant.
    - treatment_groups: List or array containing treatment groups (e.g., WORDS or EVO) for each participant.

    Returns:
    - results: Results summary of the mixed-effects linear model.
    """

    # Create a DataFrame combining connectivity data, time points, and treatment groups
    df = pd.DataFrame(connectivity_data)
    df['Time'] = time_points
    df['Group'] = treatment_groups

    # Convert time points and treatment groups to categorical variables
    df['Time'] = pd.Categorical(df['Time'])
    df['Group'] = pd.Categorical(df['Group'])

    # Define the formula for the mixed-effects model
    formula = 'Connectivity ~ Time + Group + Time:Group + (1 | Participant)'

    # Fit the mixed-effects model
    model = smf.mixedlm(formula, df, groups=df['Participant'])
    results = model.fit()

    return results

# %% Set up

home_dir = f'/media/holland/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc

# q = fmri_tools(studydir=datadir, subjectlist_text=args.subjecttextlist) # init functions and subject list

sessions = ['1','2']
runs = ['1']
rois = ['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
sites = ['NKI','UW'] # collection sites (also names of dirs)
num_subjects = 59



# %% Exclude all subjects that don't have both sessions from higher levels
# NOTE: Also manually move subject dirs that were flagged for bad anatomical scans or incidental findings (see spreadsheet)

cmd = [None]
for site in sites:
    datadir = f'{home_dir}/{site}' # where subject dirs are located
    q = fmri_tools(datadir)
    for sub in q.subs: # test
        if os.path.isfile(f'{datadir}/{sub}/func/unprocessed/rest/session_2/run_1/Rest_S2_R1_E1.nii.gz')==False:
            print(f'{sub}\n')
            cmd[0] = f'mv {datadir}/{sub} /media/holland/EVO_Estia/EVO_MRI/EXCLUDE_rest_higherlevels'
            q.exec_cmds(cmd)

# %% Read in Tx group list CSV file
with open('/home/holland/Desktop/EVO_Tx_groups.csv', mode ='r')as file:
    TxGroups = csv.reader(file)
    group_labels = []
    for line in TxGroups:
        group_labels.append(line)
        print(line)

 # %% Use lower level COPE files as columns of connectivity matrices for each session and ROI
matrix = np.zeros((902629,num_subjects)) # number of voxels by number of participants
for roi in rois:
    for session in sessions:
        i = 0 # init counter (for indexing final output matrix)
        for site in sites:
            datadir = f'{home_dir}/{site}' # where subject dirs are located
            q = fmri_tools(datadir)

            for sub in q.subs: # test
                cope_path = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/stats/cope1.nii.gz'
                if os.path.isfile(cope_path)==False:
                    print(f'\n{sub} has no lower level S{session} {roi} COPE file.\n')
                else:
                    norm_fn = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/{roi}_S{session}_cope1_normalized.nii.gz'
                    if os.path.isfile(norm_fn)==False:
                        nii = nib.load(cope_path) # read in NIFTI file
                        data = nii.get_fdata().flatten()
                        
                        # Normalize all COPE distributions
                        l2_norm = np.linalg.norm(data)
                        data_norm = data / l2_norm

                        # data_norm.tofile(norm_fn, sep=',') # save normalized vector
                        matrix[:,i] = data_norm # append to input matrix
                        i += 1 # update counter

        matrix = np.array(matrix)
        matrix_fn = f'/media/holland/EVO_Estia/EVO_rest_higherlev_vol/{roi}_S{session}_rest_higherlev_copes.csv'
        matrix.tofile(matrix_fn, sep=',')

# %% Create treatment groups list for the model





# %%

# Explanation of inputs:

#     connectivity_data: This should be a DataFrame where each row represents a participant, and each column represents a connectivity value between an ROI and whole brain. Ensure that the DataFrame has a column named 'Participant' to identify each participant uniquely.
#     time_points: This should be a list or array indicating the time points for each participant (e.g., ['pre', 'post']).
#     treatment_groups: This should be a list or array indicating the treatment group for each participant (e.g., ['WORDS', 'EVO']).

# The function fits a mixed-effects linear model using the statsmodels library, incorporating fixed effects for time points and treatment groups, as well as their interaction, and a random intercept for each participant.


# Assuming you have your connectivity data, time points, and treatment groups ready
connectivity_data = pd.DataFrame(...)  # Replace ... with your actual connectivity data
time_points = [...]  # Replace ... with your actual time points
treatment_groups = [...]  # Replace ... with your actual treatment groups

# Call the function to create the mixed-effects model
results = mixed_effects_model(connectivity_data, time_points, treatment_groups)

# Print the summary of the model results
print(results.summary())