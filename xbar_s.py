from flask import Flask, app, render_template, request, url_for, redirect, session
from fileinput import filename
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics

import detector


def xbar_s(sample_data):
    x = np.array(sample_data.iloc[:,1:].to_numpy())  
    x_bar = []
    s = [] 
    for group in x:
        x_bar.append(round(group.mean(),3))
        s.append(round(group.std(),3))
    fig, axs = plt.subplots(2, figsize=(10,10))
    constants = pd.read_excel('./assets/control_charts_constants.xlsx', sheet_name="Sheet1")
    sample_size = len(sample_data.columns) - 1
    A3 = constants.loc[constants['m'] == sample_size]['A3']
    A3 = float(A3)
    B4 = constants.loc[constants['m'] == sample_size]['B4']
    B4 = float(B4)
    B3 = constants.loc[constants['m'] == sample_size]['B3']
    B3 = float(B3)

    ## x-bar chart
    axs[0].plot(x_bar, linestyle='-', marker='o', color='black')
    axs[0].axhline((statistics.mean(x_bar)+A3*statistics.mean(s)), color='red', linestyle='dashed', label='+3 Sigma / UCL')
    axs[0].axhline((statistics.mean(x_bar)-A3*statistics.mean(s)), color='red', linestyle='dashed', label='-3 Sigma / LCL')
    axs[0].axhline((statistics.mean(x_bar)), color='blue', label='CL')
    axs[0].set_title('X-bar Chart')
    axs[0].set(xlabel='Sample', ylabel='Range')
    axs[0].legend(fancybox=True, framealpha=1, shadow=True,frameon=True, borderpad=1)

    ## S chart
    axs[1].plot(s, linestyle='-', marker='o', color='black')
    axs[1].axhline((B4*statistics.mean(s)), color='red', linestyle='dashed', label='+3 Sigma / UCL')
    axs[1].axhline((B3*statistics.mean(s)), color='red', linestyle='dashed', label='-3 Sigma / LCL')
    axs[1].axhline((statistics.mean(s)), color='blue', label='CL')
    axs[1].set_ylim(bottom=0)
    axs[1].set_title('S Chart')
    axs[1].set(xlabel='Sample', ylabel='Range')
    axs[1].legend(fancybox=True, framealpha=1, shadow=True,frameon=True, borderpad=1)

    fig.tight_layout(pad=4)

    analysis1=""
    analysis2=""

    analysis1+="X bar Chart: "
    main_arr = axs[0].lines[0].get_data()
    main_arr_df = pd.DataFrame()
    main_arr_df['x']=main_arr[0]
    main_arr_df['y']=main_arr[1]
    scatter_arr_y = []
    scatter_arr_x = []
    i = 0
    control = True
    for group in x_bar:
        if group > statistics.mean(x_bar)+A3*statistics.mean(s) or group < statistics.mean(x_bar)-A3*statistics.mean(s):
            analysis1+='{}, '.format(i+1)
            scatter_arr_y.append(main_arr_df.iloc[i][1])
            scatter_arr_x.append(main_arr_df.iloc[i][0])
            control = False
        i += 1
    if control == True:
        analysis1+='--> All points within control limits. '
    else:
        analysis1+='is/are out of control limits! '
        

    axs[0].scatter(scatter_arr_x, scatter_arr_y, marker='o', color='y', s=150)    


    analysis2+="R Chart: "
    main_arr = axs[1].lines[0].get_data()
    main_arr_df = pd.DataFrame()
    main_arr_df['x']=main_arr[0]
    main_arr_df['y']=main_arr[1]
    scatter_arr_y = []
    scatter_arr_x = []
    i = 0
    control = True
    for group in s:
        if group > B4*statistics.mean(s) or group < B3*statistics.mean(s):
            analysis2+='{}, '.format(i+1)
            scatter_arr_y.append(main_arr_df.iloc[i][1])
            scatter_arr_x.append(main_arr_df.iloc[i][0])
            control = False
        i += 1
    if control == True:
        analysis2+='-->All points within control limits. '
    else:
        analysis2+='is/are out of control limits! '

    axs[1].scatter(scatter_arr_x, scatter_arr_y, marker='o', color='y', s=150)    

        
    length_before=len(x)+1
    x=x.flatten()
    sample_group = np.repeat(range(1,length_before),sample_size)
    df = pd.DataFrame({'data':x, 'sample_group':sample_group})
    df_grouped = df.groupby('sample_group').mean()
    df_grouped.columns = ['x_bar']
    df_grouped['S'] = s
    df_grouped['x_bar_bar'] = statistics.mean(df_grouped['x_bar'])
    df_grouped['UCL'] = statistics.mean(df_grouped['x_bar'])+(A3*statistics.mean(df_grouped['S']))
    df_grouped['+2s'] = (df_grouped['UCL']-df_grouped['x_bar_bar'])/3*2+df_grouped['x_bar_bar']
    df_grouped['+1s'] = (df_grouped['UCL']-df_grouped['x_bar_bar'])/3*1+df_grouped['x_bar_bar']
    df_grouped['-1s'] = df_grouped['x_bar_bar']-(df_grouped['UCL']-df_grouped['x_bar_bar'])/3*1
    df_grouped['-2s'] = df_grouped['x_bar_bar']- (df_grouped['UCL']-df_grouped['x_bar_bar'])/3*2
    df_grouped['LCL'] = statistics.mean(df_grouped['x_bar'])-(A3*statistics.mean(df_grouped['S']))
    
    controlSay = detector.anomalyDetection(df_grouped)
    fig.savefig('./static/temp.png')   # save the figure to file    
    return analysis1, analysis2, controlSay