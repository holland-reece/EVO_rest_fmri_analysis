# EVO Resting-State Group Level Feat Model

# Holland Brown

# Updated 2024-05-11
# Created 2024-05-11

# --------------------------------------------------------------------------------------
# %%
import os
import subprocess
from my_imaging_tools import fmri_tools

# Important dirs
home_dir = f'/media/holland/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc


sessions = ['1','2']
runs = ['1']
rois = ['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
sites = ['NKI','UW'] # collection sites (also names of dirs)
# rois = ['L_rACC','R_rACC']

func_fn = 'denoised_func_data_aggr' # without extension; ac/pc aligned, denoised with ICA-AROMA
feat_fn = f'evo_rest_vol_lowerlev'
feat_df = f'{home_dir}/{feat_fn}'


#%% Run lower-level analysis using design template
cmd=[None]
commands = [None]*9
cmds = [None]*2

print(f'\n------------------------- Running Feat lower-levels -------------------------\n')

for site in sites:
    datadir = f'{home_dir}/{site}' # where subject dirs are located
    q = fmri_tools(datadir)

    if site == 'NKI':
        timestep = '1.4'
    elif site == 'UW':
        timestep = '1.399999'

    for sub in q.subs: # test
        print(f'{sub}\n')
        for session in sessions:
            # only proceed if participant has processed func file for this session
            if os.path.isdir(f'{datadir}/{sub}/func/rest/session_{session}'):
                for run in runs:
                    func_in = f'{datadir}/{sub}/func/rest/session_{session}/run_{run}/Rest_ICAAROMA/{func_fn}'
                    # print('test1')
                    if os.path.isfile(f'{func_in}_rmvols.nii.gz')==True:
                        # print(func_in)
                        
                        for roi in rois:
                            outdir = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol'

                            if os.path.isdir(outdir)==False:
                                cmd[0] = f'mkdir {outdir}'
                                q.exec_cmds(cmd)

                            # use version 2 roi txt file - was created after volumes were removed
                            roi_ts_str = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/{roi}_S{session}_R{run}_timeseries_thr0.8_v2.txt'
                            if os.path.isfile(roi_ts_str)==False:
                                q.exec_echo(f'\n{sub} does not have an extracted {roi} timeseries file.\n')

                            # Copy Fest design file to subject's ROI dir and rename
                            cmds[0] = f'cp {home_dir}/{feat_fn}_template.fsf {outdir}' # copy design file into preproc dir
                            cmds[1] = f'mv {outdir}/{feat_fn}_template.fsf {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf'
                            q.exec_cmds(cmds)
                            print(cmds[0])

                            # Search and replace variables in Feat design file
                            commands[0] = f"sed -i 's;TIMESTEP;{timestep};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                            commands[1] = f"sed -i 's;INPUTNIFTI;{func_in}_rmvols_remean.nii.gz;g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf" # needs to be remeaned version of func file
                            commands[2] = f"sed -i 's;REGIONOFINTERESTTXT;{roi_ts_str};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                            commands[3] = f"sed -i 's;REGIONOFINTEREST;{roi};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                            commands[4] = f"sed -i 's;SUBJ;{sub};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                            commands[5] = f"sed -i 's;MRISESSION;{session};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                            commands[6] = f"sed -i 's;MRIRUN;{run};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                            commands[7] = f"sed -i 's;DATADIRSTR;{datadir};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                            commands[8] = f"sed -i 's;FSLDIRSTR;{home_dir};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                            q.exec_cmds(commands)

                            q.exec_echo(f'\n-------- Running Feat analysis for {sub} --------\n')
                            cmd[0] = f'feat {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf' # Execute Feat design file
                            q.exec_cmds(cmd)

                    else:
                        print(f'File does not exist: {func_in}')

            else:
                print(f'Directory does not exist: {datadir}/{sub}/func/rest/session_{session}')

    q.exec_echo('Done.')

# %%
