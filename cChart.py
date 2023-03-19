from flask import Flask, app, render_template, request, url_for, redirect, session
from fileinput import filename
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics

import detector


def xbar_r(sample_data):
    x = np.array(sample_data.iloc[:,1:].to_numpy())  
    x_bar = []
    r = [] 
    for group in x:
        x_bar.append(round(group.mean(),3))
        r.append(round(group.max() - group.min(),3))
    fig, axs = plt.subplots(2, figsize=(10,10))
    constants = pd.read_excel('./assets/control_charts_constants.xlsx', sheet_name="Sheet1")
    sample_size = len(sample_data.columns) - 1
    A2 = constants.loc[constants['m'] == sample_size]['A2']
    A2 = float(A2)
    D4 = constants.loc[constants['m'] == sample_size]['D4']
    D4 = float(D4)
    D3 = constants.loc[constants['m'] == sample_size]['D3']
    D3 = float(D3)
    sigma = np.std(x_bar)

    ## x-bar chart
    axs[0].plot(x_bar, linestyle='-', marker='o', color='black')
    axs[0].axhline((statistics.mean(x_bar)+A2*statistics.mean(r)), color='darkred', linestyle='dashed', label='+3 Sigma / UCL')
    axs[0].axhline((statistics.mean(x_bar)-A2*statistics.mean(r)), color='darkgreen', linestyle='dashed', label='-3 Sigma / LCL')
    axs[0].axhline((statistics.mean(x_bar)), color='blue', label='CL')
    axs[0].set_title('X-bar Chart')
    axs[0].set(xlabel='Sample', ylabel='Range')
    axs[0].legend(fancybox=True, framealpha=1, shadow=True,frameon=True, borderpad=1)

    ## R chart
    axs[1].plot(r, linestyle='-', marker='o', color='black')
    axs[1].axhline((D4*statistics.mean(r)), color='darkred', linestyle='dashed', label='+3 Sigma / UCL')
    axs[1].axhline((D3*statistics.mean(r)), color='darkgreen', linestyle='dashed', label='-3 Sigma / LCL')
    axs[1].axhline((statistics.mean(r)), color='blue', label='CL')
    axs[1].set_ylim(bottom=0)
    axs[1].set_title('R Chart')
    axs[1].set(xlabel='Sample', ylabel='Range')
    axs[1].legend(fancybox=True, framealpha=1, shadow=True,frameon=True, borderpad=1)

    fig.tight_layout(pad=4)

    analysis=""

    # print("X bar Chart:")
    analysis+="X bar Chart:\n"
    main_arr = axs[0].lines[0].get_data()
    main_arr_df = pd.DataFrame()
    main_arr_df['x']=main_arr[0]
    main_arr_df['y']=main_arr[1]
    scatter_arr_y = []
    scatter_arr_x = []
    i = 0
    control = True
    for group in x_bar:
        if group > statistics.mean(x_bar)+A2*statistics.mean(r) or group < statistics.mean(x_bar)-A2*statistics.mean(r):
            analysis+='-->Sample {} out of mean control limits!\n'.format(i+1)
            scatter_arr_y.append(main_arr_df.iloc[i][1])
            scatter_arr_x.append(main_arr_df.iloc[i][0])
            control = False
        i += 1
    if control == True:
        analysis+='-->All points within control limits.\n'

    axs[0].scatter(scatter_arr_x, scatter_arr_y, marker='o', color='y', s=150)    
        
    # print("R Chart")
    analysis+="R Chart:\n"
    main_arr = axs[1].lines[0].get_data()
    main_arr_df = pd.DataFrame()
    main_arr_df['x']=main_arr[0]
    main_arr_df['y']=main_arr[1]
    scatter_arr_y = []
    scatter_arr_x = []
    i = 0
    control = True
    for group in r:
        if group > D4*statistics.mean(r):
            analysis+='-->Sample {} out of range control limits!\n'.format(i+1)
            scatter_arr_y.append(main_arr_df.iloc[i][1])
            scatter_arr_x.append(main_arr_df.iloc[i][0])
            control = False
        i += 1
    if control == True:
        analysis+='-->All points within control limits.\n'

    axs[1].scatter(scatter_arr_x, scatter_arr_y, marker='o', color='y', s=150)    


    length_before=len(x)+1
    x=x.flatten()
    sample_group = np.repeat(range(1,length_before),sample_size)
    df = pd.DataFrame({'data':x, 'sample_group':sample_group})
    df_grouped = df.groupby('sample_group').mean()
    df_grouped.columns = ['x_bar']
    df_max = df.groupby('sample_group').max()
    df_min = df.groupby('sample_group').min()
    df_grouped['R'] = df_max['data'] - df_min['data']
    df_grouped['x_bar_bar'] = statistics.mean(df_grouped['x_bar'])
    df_grouped['UCL'] = statistics.mean(df_grouped['x_bar'])+(A2*statistics.mean(df_grouped['R']))
    df_grouped['+2s'] = (df_grouped['UCL']-df_grouped['x_bar_bar'])/3*2+df_grouped['x_bar_bar']
    df_grouped['+1s'] = (df_grouped['UCL']-df_grouped['x_bar_bar'])/3*1+df_grouped['x_bar_bar']
    df_grouped['-1s'] = df_grouped['x_bar_bar']-(df_grouped['UCL']-df_grouped['x_bar_bar'])/3*1
    df_grouped['-2s'] = df_grouped['x_bar_bar']- (df_grouped['UCL']-df_grouped['x_bar_bar'])/3*2
    df_grouped['LCL'] = statistics.mean(df_grouped['x_bar'])-(A2*statistics.mean(df_grouped['R']))
    # print("\nFrom Control Chart Rules:")
    controlSay = detector.anomalyDetection(df_grouped)
    return analysis, controlSay, fig