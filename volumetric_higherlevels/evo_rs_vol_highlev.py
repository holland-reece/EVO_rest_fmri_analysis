# %%
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from my_imaging_tools import fmri_tools


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

# %%
# Important dirs
home_dir = f'/media/holland/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc

# q = fmri_tools(studydir=datadir, subjectlist_text=args.subjecttextlist) # init functions and subject list

sessions = ['1','2']
runs = ['1']
rois = ['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
sites = ['NKI','UW'] # collection sites (also names of dirs)
# rois = ['L_rACC','R_rACC']

func_fn = 'denoised_func_data_aggr' # without extension; ac/pc aligned, denoised with ICA-AROMA
feat_fn = f'evo_rest_vol_lowerlev'
feat_df = f'{home_dir}/{feat_fn}'

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