from flask import Flask, app, render_template, request, url_for, redirect, session
from fileinput import filename
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics

import detector


def xmR(sample_data):
    x = np.array(sample_data.iloc[:,1:].to_numpy())
    mR=[np.nan]
    i = 1
    for data in range(1, len(x)):
        mR.append(abs(x[i] - x[i-1]))
        i += 1
    mR = pd.Series(mR)
    mR=mR.str[0]
    x = pd.Series(x.tolist())
    x=x.str[0]
    data = pd.concat([x,mR], axis=1).rename(columns={0:"x", 1:"mR"})
    # plt.figure(figsize=(10,5))
    fig, axs = plt.subplots(2, figsize=(10,10))

    axs[0].plot(data['x'], linestyle='-', marker='o', color='black')
    axs[0].axhline(statistics.mean(data['x'])+3*statistics.mean(data['mR'][1:len(data['mR'])])/1.128, color = 'red', linestyle = 'dashed', label='+3 Sigma / UCL')
    axs[0].axhline(statistics.mean(data['x'])+2*statistics.mean(data['mR'][1:len(data['mR'])])/1.128, color = 'limegreen', linestyle = 'dashed', label='+2 Sigma / UCL')
    axs[0].axhline(statistics.mean(data['x'])+1*statistics.mean(data['mR'][1:len(data['mR'])])/1.128, color = 'hotpink', linestyle = 'dashed', label='+1 Sigma / UCL')
    axs[0].axhline(statistics.mean(data['x'])-1*statistics.mean(data['mR'][1:len(data['mR'])])/1.128, color = 'hotpink', linestyle = 'dashed', label='-1 Sigma / LCL')
    axs[0].axhline(statistics.mean(data['x'])-2*statistics.mean(data['mR'][1:len(data['mR'])])/1.128, color = 'limegreen', linestyle = 'dashed', label='-2 Sigma / LCL')
    axs[0].axhline(statistics.mean(data['x'])-3*statistics.mean(data['mR'][1:len(data['mR'])])/1.128, color = 'red', linestyle = 'dashed', label='-3 Sigma / LCL')
    axs[0].axhline(statistics.mean(data['x']), color='blue', label="CL")
    axs[0].set_title('X Chart')
    axs[0].set(xlabel='Sample',ylabel='Range')
    axs[0].legend(fancybox=True, framealpha=1, shadow=True,frameon=True, borderpad=1)

    axs[1].plot(data['mR'], linestyle='-', marker='o', color='black')
    axs[1].axhline(statistics.mean(data['mR'][1:len(data['mR'])])+3*statistics.mean(data['mR'][1:len(data['mR'])])*0.8525, color='red', linestyle ='dashed', label='+3 Sigma / UCL')
    axs[1].axhline(statistics.mean(data['mR'][1:len(data['mR'])])+2*statistics.mean(data['mR'][1:len(data['mR'])])*0.8525, color='limegreen', linestyle ='dashed', label='+2 Sigma')
    axs[1].axhline(statistics.mean(data['mR'][1:len(data['mR'])])+1*statistics.mean(data['mR'][1:len(data['mR'])])*0.8525, color='hotpink', linestyle ='dashed', label='+1 Sigma')
    axs[1].axhline(statistics.mean(data['mR'][1:len(data['mR'])])-1*statistics.mean(data['mR'][1:len(data['mR'])])*0.8525, color='hotpink', linestyle ='dashed', label='-1 Sigma')
    axs[1].axhline(statistics.mean(data['mR'][1:len(data['mR'])])-2*statistics.mean(data['mR'][1:len(data['mR'])])*0.8525, color='limegreen', linestyle ='dashed', label='-2 Sigma')
    axs[1].axhline(statistics.mean(data['mR'][1:len(data['mR'])])-3*statistics.mean(data['mR'][1:len(data['mR'])])*0.8525, color='red', linestyle ='dashed', label='-3 Sigma / LCL')
    axs[1].axhline(statistics.mean(data['mR'][1:len(data['mR'])]), color='blue', label="CL")
    axs[1].set_title('mR Chart')
    axs[1].set(xlabel='Sample',ylabel='Range')
    axs[1].legend(fancybox=True, framealpha=1, shadow=True,frameon=True, borderpad=1)

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
    for unit in data['x']:
        if unit > statistics.mean(data['x'])+3*statistics.mean(data['mR'][1:len(data['mR'])])/1.128 or unit < statistics.mean(data['x'])-3*statistics.mean(data['mR'][1:len(data['mR'])])/1.128:
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
    for unit in data['mR']:
        if unit > statistics.mean(data['mR'][1:len(data['mR'])])+3*statistics.mean(data['mR'][1:len(data['mR'])])*0.8525 or unit < statistics.mean(data['mR'][1:len(data['mR'])])-3*statistics.mean(data['mR'][1:len(data['mR'])])*0.8525:
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
        
    df_grouped = pd.DataFrame()
    df_grouped['x_bar']=data['x']
    df_grouped.index = np.arange(1, len(df_grouped) + 1)
    df_grouped['x_bar_bar'] = statistics.mean(data['x'])
    df_grouped['UCL'] = statistics.mean(data['x'])+3*statistics.mean(data['mR'][1:len(data['mR'])])/1.128
    df_grouped['+2s'] = statistics.mean(data['x'])+2*statistics.mean(data['mR'][1:len(data['mR'])])/1.128
    df_grouped['+1s'] = statistics.mean(data['x'])+1*statistics.mean(data['mR'][1:len(data['mR'])])/1.128
    df_grouped['-1s'] = statistics.mean(data['x'])-1*statistics.mean(data['mR'][1:len(data['mR'])])/1.128
    df_grouped['-2s'] = statistics.mean(data['x'])-2*statistics.mean(data['mR'][1:len(data['mR'])])/1.128
    df_grouped['LCL'] = statistics.mean(data['x'])-3*statistics.mean(data['mR'][1:len(data['mR'])])/1.128
    
    controlSay = detector.anomalyDetection(df_grouped)
    fig.savefig('./static/temp.png')   # save the figure to file
    return analysis1, analysis2, controlSay