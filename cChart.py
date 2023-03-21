from flask import Flask, app, render_template, request, url_for, redirect, session
from fileinput import filename
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics

import detector


def cChart(sample_data):
    c = sample_data
    plt.figure(figsize=(10,5))
    plt.plot(c[1], linestyle='-', marker='o', color='black')
    plt.axhline(statistics.mean(c[1])+3*np.sqrt(statistics.mean(c[1])), color='red', linestyle='dashed', label='+3 Sigma / UCL')
    plt.axhline(statistics.mean(c[1])+2*np.sqrt(statistics.mean(c[1])), color='limegreen', linestyle='dashed', label='+2 Sigma')
    plt.axhline(statistics.mean(c[1])+1*np.sqrt(statistics.mean(c[1])), color='hotpink', linestyle='dashed', label='+1 Sigma')
    plt.axhline(statistics.mean(c[1])-1*np.sqrt(statistics.mean(c[1])), color='hotpink', linestyle='dashed', label='-1 Sigma')
    plt.axhline(statistics.mean(c[1])-2*np.sqrt(statistics.mean(c[1])), color='limegreen', linestyle='dashed', label='-2 Sigma')
    plt.axhline(statistics.mean(c[1])-3*np.sqrt(statistics.mean(c[1])), color='red', linestyle='dashed', label='-3 Sigma / LCL')
    plt.axhline(statistics.mean(c[1]), color='blue', label='CL')
    plt.ylim(bottom=0)
    plt.title('C Chart')
    plt.xlabel('Sample No.')
    plt.ylabel('Defect Count')
    plt.legend(fancybox=True, framealpha=1, shadow=True,frameon=True, borderpad=1)

    analysis1=""
    analysis2=""
    
    print("C Chart:")
    ax = plt.gca()
    main_arr = ax.lines[0].get_data()
    main_arr_df = pd.DataFrame()
    main_arr_df['x']=main_arr[0]
    main_arr_df['y']=main_arr[1]
    scatter_arr_y = []
    scatter_arr_x = []
    i = 0
    control = True
    for group in c[1]:
        if group > statistics.mean(c[1])+3*np.sqrt(statistics.mean(c[1])) or group < statistics.mean(c[1])-3*np.sqrt(statistics.mean(c[1])):
            analysis1+='{}, '.format(i+1)
            scatter_arr_y.append(main_arr_df.iloc[i][1])
            scatter_arr_x.append(main_arr_df.iloc[i][0])
            control = False
        i += 1
    if control == True:
        analysis1+='--> All points within control limits. '
    else:
        analysis1+='is/are out of control limits! '
        
    plt.scatter(scatter_arr_x, scatter_arr_y, marker='o', color='y', s=150)        
    
    c=c[1]
    df_grouped = pd.DataFrame()
    df_grouped['x_bar']=c
    df_grouped.index = np.arange(1, len(df_grouped) + 1)
    df_grouped['x_bar_bar'] = statistics.mean(df_grouped['x_bar'])
    df_grouped['UCL'] = statistics.mean(df_grouped['x_bar_bar'])+3*np.sqrt(df_grouped['x_bar_bar'])
    df_grouped['+2s'] = statistics.mean(df_grouped['x_bar_bar'])+2*np.sqrt(df_grouped['x_bar_bar'])
    df_grouped['+1s'] = statistics.mean(df_grouped['x_bar_bar'])+1*np.sqrt(df_grouped['x_bar_bar'])
    df_grouped['-1s'] = statistics.mean(df_grouped['x_bar_bar'])-1*np.sqrt(df_grouped['x_bar_bar'])
    df_grouped['-2s'] = statistics.mean(df_grouped['x_bar_bar'])-2*np.sqrt(df_grouped['x_bar_bar'])
    df_grouped['LCL'] = statistics.mean(df_grouped['x_bar_bar'])-3*np.sqrt(df_grouped['x_bar_bar'])

    controlSay = detector.anomalyDetection(df_grouped)
    plt.savefig('./static/temp.png')   # save the figure to file
    return analysis1, analysis2, controlSay