# EVO Post-MEP Resting-State Higher-Level (Level 2 Between-Runs) Fixed Effects Linear Model Using FSL Feat

# Holland Brown

# Updated 2024-05-21
# Created 2024-05-21

# --------------------------------------------------------------------------------------
# %%
import os
import subprocess
from my_imaging_tools import fmri_tools

# Important dirs
home_dir = f'/media/holland/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc

# q = fmri_tools(studydir=datadir, subjectlist_text=args.subjecttextlist) # init functions and subject list

sessions = ['1','2']
rois = ['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
sites = ['NKI','UW'] # collection sites (also names of dirs)

feat_fn = f'level2'
feat_df = f'/media/holland/EVO_Estia/EVO_rest_analyses/EVO_level2_betweenruns/{feat_fn}'


#%% Run lower-level analysis using design template (ref: first_level5.sh)
cmd=[None]
commands = [None]*3
cmds = [None]*2

# print(f'\n------------------------- Running Feat lower-levels -------------------------\n')

for site in sites:
    datadir = f'{home_dir}/{site}' # where subject dirs are located
    q = fmri_tools(datadir)

    for sub in q.subs:
        for roi in rois:
            outdir = f'{home_dir}/{site}/{sub}/func/rest/rois/{roi}'

            # Copy Fest design file to subject's ROI dir and rename
            cmds[0] = f'cp {feat_df}_template.fsf {outdir}' # copy design file into preproc dir
            cmds[1] = f'mv {outdir}/{feat_fn}_template.fsf {outdir}/{sub}_{feat_fn}_level2_betweenruns.fsf' # rename design file
            q.exec_cmds(cmds)

            commands[0] = f"sed -i 's;MRI_SITE;{site};g' {outdir}/{sub}_{feat_fn}_level2_betweenruns.fsf"
            commands[1] = f"sed -i 's;REGIONOFINTEREST;{roi};g' {outdir}/{sub}_{feat_fn}_level2_betweenruns.fsf"
            commands[2] = f"sed -i 's;SUBJ_ID;{sub};g' {outdir}/{sub}_{feat_fn}_level2_betweenruns.fsf"
            q.exec_cmds(commands)

            q.exec_echo(f'\n-------- Running Feat analysis for {roi}, {sub} --------\n')
            cmd[0] = f'feat {outdir}/{sub}_{feat_fn}_level2_betweenruns.fsf' # Execute Feat design file
            q.exec_cmds(cmd)

    q.exec_echo('Done.')

# %%
