# EVO Task-Based fMRI: Create Task Onset Text Files as Expected by FSL Feat

# Holland Brown

# Updated 2024-06-04
# Created 2024-06-03

# NOTE: refer to Oded Bein's jupyter notebook for creating task onset files
    # see Oded's example onset file for a task with 16 conditions

# NOTE: for EVO study's Floop (Stroop with Flankers) task, there are 4 conditions

""" Oded's notes about his code:

So, this is actually an overly complicated script bc in that experiment we had 16 trials, 
and there were bugs in the code that ran the study and how it logged in participants misses/errors
(data collected before I joined the lab, you can see I have experience with taking over projects  ). 
The thing I think that is most relevant to you is this function:

create_all16states_onsets

and the loop in the chunk called "Create onsets for all subjects, all 16 states model". The loops 
takes in a behavioral file per participant, then split it to runs because in my study, all runs were 
saved in one behaivoral file, and then calls the function above.
 
In the function "create_all16states_onsets", there's a lot of junk you won't need. But basically
"states" in that code are the different conditions, so it created a file per each state, and then 
a file for errors. I think the most relevant parts are the beginning where I define some things, and 
then the loop under:

### for each state, create onsets file:
And you can see how I created the trash regressor in addition to a file per state/condition.

Also note that I used RTs as the duration column. I'll ask Lindsay whether the duration should be 
the trial duraion or the RT, as this is task dependent. I also attach a behavior file if it's useful 
to understand the code.

"""

# --------------------------------------------------------------------------------------
# %% Import packages
import os
import subprocess
import numpy as np
import pandas as pd
import os
import csv
import warnings
from scipy.io import loadmat
import scipy.stats as stats
import glob
import math
from my_imaging_tools import fmri_tools

# %% Define functions
def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier


#creates onsets per run:
def create_all16states_onsets(curr_df,sub_onsets_dir,r,chk_md,subj):
    #define the name of the model:
    model = 'all_16states'
    ### clean up ###
    #RTs need to be in seconds for the duration, and lets align all to have 3 digits:
    curr_df['rt'] = (curr_df['rt']/1000).map('{:,.3f}'.format)
    #the timing of all should be aligned, so let's make it all up to 3 digits after the dot:
    curr_df['tstimon'] = curr_df['tstimon'].map('{:,.3f}'.format)
    
    ##add cong/incong:
    dimA = curr_df['dimA'].values
    dimB = curr_df['dimB'].values
    cong=[]
    for i in list(range(len(dimA))):
        if dimA[i][1] == dimB[i][1]:
            cong.append('cong')
        else:
            cong.append('incong')
    curr_df['congruency'] = cong
    
    #get indices of where there are errors marked in the behavioral files:
    er_t=curr_df.index[curr_df['error'] != 0] 
    #print(er_t)
    if (er_t.empty):
        print('no errors')
    
    #mark one trial before the trial that is marked as an error as error:
    #this should not be done for the last error, in cases where there are two consecutive errors:
    #copy er_t (I don't want to use er_t for that, because I still want the loop below to go through it, for checking)
    print(er_t[:])
    er_tc=np.array(er_t).astype("float")
    #go through er_tc and remove the first error from two consecuitive trials, or the second, if answers the condition below:
    #go through er_t, so that er_tc can be changed independently - no problems with marking nan in first/second
    for ier in list(range(len(er_t))):
        if ier < (len(er_t)-1): #check until the last before one (implemented like this and not in the loop bc of the part I commented out below)
            if er_t[ier+1] - er_t[ier]  == 1: #this is the first of two consecuitive
                print('first of two consecuitive trials is: ' + curr_df.loc[er_t[ier],'cond'])
                print('second of two consecuitive trials is: ' + curr_df.loc[er_t[ier+1],'cond'])
                #if the second one is DCSA/DCDA, or the first is DCSA:
                if ((curr_df.loc[er_t[ier],'cond'] == 'DCSA') | 
                    (curr_df.loc[er_t[ier+1],'cond'] == 'DCSA') | (curr_df.loc[er_t[ier+1],'cond']=='DCDA')):
                    print('first/second of two consecuitive trials is a category switch')
                    print("Need to mark the trial before the first error as error (SO DO NOT exclude from er_tc)")
                elif ((curr_df.loc[er_t[ier],'cond'] == 'DCDA') & (curr_df.loc[er_t[ier+1],'cond'] == 'SCDA') & (curr_df.loc[er_t[ier],'congruency'] == 'incong')):
                    print('first of two consecuitive trials is DCDA and incong, second is SCDA')
                    print("Need to mark the trial before the first error as error (SO DO NOT exclude from er_tc)")
                elif ((curr_df.loc[er_t[ier],'cond'] == 'SCSA') & (curr_df.loc[er_t[ier+1],'cond'] == 'SCSA')):
                    print('curr trial: ' + str(curr_df.loc[er_t[ier],'btrial']) + ' error: ' + str(curr_df.loc[er_t[ier],'error']) + ' congruency: ' + str(curr_df.loc[er_t[ier],'congruency']))
                    print('next trial: ' + str(curr_df.loc[er_t[ier+1],'btrial']) + ' error: ' + str(curr_df.loc[er_t[ier+1],'error']) + ' congruency: ' + str(curr_df.loc[er_t[ier +1],'congruency']))
                    if (curr_df.loc[er_t[ier],'congruency'] == 'cong'):
                        print('cong first of two consecuitive trials that are SCSA')
                        print("DO NOT mark the trial before the first error as error (exclude from er_tc)")
                        er_tc[ier] = 'nan'
                    else: #an incong trial:
                        if (curr_df.loc[er_t[ier],'error'] == 2) & (curr_df.loc[er_t[ier+1],'error'] == 1):
                            print('first of two consecuitive trials that are SCSA. errors are 2 then 1')
                            print("Need to mark the trial before the first error as error (SO DO NOT exclude from er_tc)")
                        elif (curr_df.loc[er_t[ier]-1,'cond'] == 'SCSA'):
                            #not 2,1 - depends on the previous trial - if SCSA - no need to exclude
                            print('first of two consecuitive trials that are SCSA. prev is SCSA') #errors are 2 then 1
                            print("DO NOT mark the trial before the first error as error (exclude from er_tc)")
                            er_tc[ier] = 'nan'
                        elif ((curr_df.loc[er_t[ier]-1,'cond'] == 'DCSA') | (curr_df.loc[er_t[ier]-1,'cond']=='DCDA')):
                            print('first of two consecuitive trials that are SCSA. prev is DCSA/DCDA')
                            print("Need to mark the trial before the first error as error (SO DO NOT exclude from er_tc)") 
                        else:
                              print("might be a scenario I didn't check, check code")

                else: #if none of the above, generally do not mark:
                    print("DO NOT mark the trial before the first error as error (exclude from er_tc)")
                    er_tc[ier] = 'nan'

        #if the second of two consecutive trials,which fullfile these conditions, exclude so that we do not change the error from 2 to 1.         
        if ((ier > 0) & ((er_t[ier] - er_t[ier-1])  == 1)): #this is the second of two consecuitive
            if ((curr_df.loc[er_t[ier-1],'cond'] == 'SCSA') & (curr_df.loc[er_t[ier],'cond'] == 'SCSA')):
                print('second of two error trials where the first and second are SCSA')
                print("need to exclude the second trial from er_tc, so that it'll not change the 2 to 1")
                er_tc[ier] = 'nan'

    #if the first trial is an error:
    if ((curr_df.loc[curr_df['btrial'] == 1, 'error'] != 0).bool()):
        print('first trial is an error, remove from er_tc so it does not cause problems\n' + 
        'with marking er_tc-1 trials')
        er_tc=er_tc[1:]
        #if the first is not an error, mark as one:
    else:
        #if not already an error, include the first trial in a trash bin
        #by marking the first trial as an error:
        curr_df.loc[curr_df['btrial'] == 1, 'error'] = 1 
        
    er_tc=er_tc[~np.isnan(er_tc)].astype(int)
    print(er_tc)
    curr_df.loc[er_tc-1,'error']=1 #if empty - won't do a thing :)

    ### compute the state based on same and prior step, and attach to curr_df ####
    curr_t = np.array(curr_df['dimA'][1:])
    prev_t = np.array(curr_df['dimA'][0:-1])
    state = prev_t + curr_t #this is prev trial,curr trial
    #it's parallel to how it is in the paper: e.g., (Ho)Fo, only I didn't include the parantheses
    all_states = np.unique(state)
    state = np.insert(state,0,np.nan)
    curr_df['state'] = state
    
    
    #find the shortest time gap - we'll add that to calculate the timing of the missing trials:
    curr_t = np.array(curr_df['tstimon'][1:])
    prev_t = np.array(curr_df['tstimon'][0:-1])
    #min_time=round_down(min(curr_t.astype(np.float)-prev_t.astype(np.float)),2) #used to define it by this - but didn't work well because depends on RT - better taking it from what is pre-difined
    min_time=min_time=round_down(min(curr_df['soa'][1:]),2) #that defines the minimal time to pass - no trial should be shorter than that
    print('min time is: ' + str(min_time))
    
    ### for each state, create onsets file:
    for st in all_states:
        curr_st = curr_df[(curr_df['state'] == st) & (curr_df['error'] == 0)] 
        onsets = curr_st[['tstimon','rt']]
        onsets['modulation'] = 1
        if chk_md == 1:
            #print how many trials are in the current state: 
            print('#trials in state {st}: {n}'.format(st=st,n=curr_st.shape[0]))
        else:
            #save file:
            onsetsfile = '{o_dir}/{m}_run{r}_{st}.txt'.format(o_dir=sub_onsets_dir, m=model,r=r,st=st)
            onsets.to_csv(onsetsfile,sep='\t',index=False, header = False)
    
    ### create the trash regressor for the first trial and mistakes:
    curr_st = curr_df[(curr_df['error'] != 0)] 
    onsets = curr_st[['tstimon','rt']]
    
    #change 'tstimon' in curr_df to numeric so I can add and subtract to it:
    curr_df['tstimon'] = pd.to_numeric(curr_df['tstimon'],downcast="float") 
    
    #add the onsets for the missing trials:
    prev_time=[]
    duration=[]
    
    for ier in range(len(er_t)):
        curr_er = er_t[ier]
        print('working on error trial: ' + str(curr_df.loc[curr_er,'btrial']))
        if ier == (len(er_t)-1): #this is the last error
            #this is the last error, cannot be the first of consecuitive, just add the onsets:
            add_error_onsets(curr_df,curr_er,prev_time,duration,min_time)
        else: #this is not the last error, check if the first of consecuitive: 
            if er_t[ier+1] - curr_er  == 1: #if so: 
                print('the first of two consecuitive errors, time difference is:')
                print(curr_df.loc[er_t[ier+1],'tstimon'] - curr_df.loc[curr_er,'tstimon'])
                print('curr cond is: ' + curr_df.loc[er_t[ier],'cond'] + ' second is: ' + curr_df.loc[er_t[ier+1],'cond'])

                if ((ier > 0) & (curr_er - er_t[ier-1] == 1)): #this might be a middle one, check for middle of three consec errors - treat differently:
                    print('Middle trial in a SEQUENCE OF THREE ERROR, CHECK CODE. marks changes')
                    #if category switch - might be different, raise excpetion:
                    #I now checked it (subj 110) - need to mark previous changes anyway, left her for reference
                    #if ((curr_df.loc[curr_er,'cond'] == 'DCSA') | (curr_df.loc[curr_er,'cond']=='DCDA')):
                    #   raise Exception("Middle trial in a sequence of three errors is a category switch, check code")
                    if ((subj == 108) & (r == 1) & (curr_df.loc[curr_er,'btrial'] != 2)): #if it's the seconf one, need to mark the time before the first trial
                        print('sub 108, begining, no need to mark changes')
                    elif ((subj == 134) & (r == 2) & (curr_df.loc[er_t[ier],'cond'] == 'SCSA')): 
                        print('sub 134, 4 trials, no need to mark changes')
                    else:
                        #middle of three errors, need to mark previous changes:
                        add_error_onsets(curr_df,curr_er,prev_time,duration,min_time)

                else: #ier == 0, so this cannot be the first of three errors, or ier >0, but only the first of two:
                    if ((curr_df.loc[er_t[ier+1],'cond'] == 'DCSA') | (curr_df.loc[er_t[ier+1],'cond']=='DCDA')):
                        print('the first of two consecuitive errors (not middle of three), second is a category switch, mark previous errors')
                        add_error_onsets(curr_df,curr_er,prev_time,duration,min_time)
                        #if  (curr_df.loc[er_t[ier+1],'cond']=='DCDA'):
                        #    print('next error is: ' + curr_df.loc[er_t[ier+1],'cond'] + ' check that indeed needs to mark errors')
                    elif ((curr_df.loc[er_t[ier],'cond'] == 'SCSA') & (curr_df.loc[er_t[ier+1],'cond'] == 'SCSA')):
                        if (curr_df.loc[er_t[ier],'congruency'] == 'cong'):
                            print('cong first of two consecuitive trials that are SCSA')
                            print('NOT marking additional errors')
                        else: #an incong trial:
                            if (curr_df.loc[er_t[ier],'error'] == 2) & (curr_df.loc[er_t[ier]+1,'error'] == 1):
                                print('first of two consecuitive trials that are SCSA. errors are 2 then 1. mark previous errors')
                                add_error_onsets(curr_df,curr_er,prev_time,duration,min_time)
                            elif (curr_df.loc[er_t[ier]-1,'cond'] == 'SCSA'):
                                #not 2,1 - depends on the previous trial - if SCSA - no need to exclude
                                print('first of two consecuitive trials that are SCSA. prev is SCSA') #errors are 2 then 1
                                print('NOT marking additional errors')
                            elif ((curr_df.loc[er_t[ier]-1,'cond'] == 'DCSA') | (curr_df.loc[er_t[ier]-1,'cond']=='DCDA')):
                                print('first of two consecuitive trials that are SCSA. prev is DC. mark previous errors')
                                add_error_onsets(curr_df,curr_er,prev_time,duration,min_time)
                            else:
                                  print("might be a scenario I didn't check, check code")

                    else: #not a special case of two consecuitive errors
                        print('first trial of two consecuitive errors, not a special case')
                        print('NOT marking additional errors')

            else: #if not the first of two consecuitive trials (i.e., the second, or a single one), add onsets:
                add_error_onsets(curr_df,curr_er,prev_time,duration,min_time)


    
    temp_ons = pd.DataFrame({"tstimon": prev_time,'rt': duration})
    onsets = onsets.append(temp_ons)
    #change to numeric so I can sort:
    onsets['tstimon'] = pd.to_numeric(onsets['tstimon'],downcast="float") 
    onsets=onsets.sort_values(by=['tstimon'])
    
    ## check first trial:
    if (onsets.iloc[0,onsets.columns.get_loc('tstimon')] > 10):
        
        print('*** CHECK FIRST TRIAL, dur is: %.3f ***' % onsets.iloc[0,onsets.columns.get_loc('tstimon')])
    #ls = [type(item) for item in onsets['tstimon']]
    #print(ls)
    
    #format nicely:
    onsets['rt'] = pd.to_numeric(onsets['rt'],downcast="float").map('{:,.3f}'.format)
    onsets['tstimon'] = onsets['tstimon'].map('{:,.3f}'.format)
    
    #if there are three consecuitive errors, hard to say in advance when to mark changes or not
    #becuase it depends on the specific sequence of trials. So I added this to exclude if marked twice:
    onsets=onsets.drop_duplicates()
    
    #add modulation
    onsets['modulation'] = 1
    print(onsets)
    #save to a file
    if chk_md == 0:
        #save file:
        onsetsfile = '{o_dir}/{m}_run{r}_trash.txt'.format(o_dir=sub_onsets_dir, m=model,r=r)
        onsets.to_csv(onsetsfile,sep='\t',index=False, header = False)

#set pandas option:
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

# Important dirs
# home_dir = f'/media/holland/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc
home_dir = f'/Volumes/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc
onset_excel_path = f'' # dir containing excel files with onset times for each subject

sessions = ['1','2'] # for Floop, there are 2 sessions (for most participants)
runs = ['1','2'] # for Floop, there are 2 runs
sites = ['NKI','UW'] # collection sites (also names of dirs)
task_name = 'floop' # task name as it appears in directories

# %%
command = [None]*2
for site in sites:
    datadir = f'{home_dir}/{site}'
    q = fmri_tools(datadir)
    for sub in q.subs:
        for session in sessions:
            for run in runs:
                onsetfile_path = f'{datadir}/{sub}/func/unprocessed/task/{task_name}/session_{session}/run_{run}'
                command[0] = f'touch {onsetfile_path}/{task_name}_S{session}_R{run}_onset.txt' # create empty text file
