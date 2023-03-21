from flask import Flask, app, render_template, request, url_for, redirect, session
from fileinput import filename
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics
import pylab

import detector


def pChart(sample_data):
    p=sample_data
    p['p'] = p[1]/p['sample_size']

    # Plot p-chart
    plt.figure(figsize=(10,5))
    plt.plot(p['p'], linestyle='-', marker='o', color='black')
    plt.step(x=range(0,len(p['p'])), y=statistics.mean(p['p'])+3*(np.sqrt((statistics.mean(p['p'])*(1-statistics.mean(p['p'])))/(p['sample_size']))), color='red', linestyle='dashed', label='+3 Sigma / UCL')
    plt.step(x=range(0,len(p['p'])), y=statistics.mean(p['p'])+2*(np.sqrt((statistics.mean(p['p'])*(1-statistics.mean(p['p'])))/(p['sample_size']))), color='limegreen', linestyle='dashed', label='+2 Sigma')
    plt.step(x=range(0,len(p['p'])), y=statistics.mean(p['p'])+1*(np.sqrt((statistics.mean(p['p'])*(1-statistics.mean(p['p'])))/(p['sample_size']))), color='hotpink', linestyle='dashed', label='+1 Sigma')
    plt.step(x=range(0,len(p['p'])), y=statistics.mean(p['p'])-1*(np.sqrt((statistics.mean(p['p'])*(1-statistics.mean(p['p'])))/(p['sample_size']))), color='hotpink', linestyle='dashed', label='-1 Sigma')
    plt.step(x=range(0,len(p['p'])), y=statistics.mean(p['p'])-2*(np.sqrt((statistics.mean(p['p'])*(1-statistics.mean(p['p'])))/(p['sample_size']))), color='limegreen', linestyle='dashed', label='-2 Sigma')
    plt.step(x=range(0,len(p['p'])), y=statistics.mean(p['p'])-3*(np.sqrt((statistics.mean(p['p'])*(1-statistics.mean(p['p'])))/(p['sample_size']))), color='red', linestyle='dashed', label='-3 Sigma / LCL')
    plt.axhline(statistics.mean(p['p']), color='blue', label="CL")
    plt.ylim(bottom=0)
    plt.title('p Chart')
    plt.xlabel('Group')
    plt.ylabel('Fraction Defective')
    # plt.legend(fancybox=True, framealpha=1, shadow=True,frameon=True, borderpad=1)

    ax = plt.gca()
    

    analysis1=""
    analysis2=""

    analysis1+="P Chart: "
    main_arr = ax.lines[0].get_data()
    main_arr_df = pd.DataFrame()
    main_arr_df['x']=main_arr[0]
    main_arr_df['y']=main_arr[1]
    scatter_arr_y = []
    scatter_arr_x = []
    i = 0
    control = True
    for group in p['p']:
        if group > (statistics.mean(p['p'])+3*(np.sqrt((statistics.mean(p['p'])*(1-statistics.mean(p['p'])))/statistics.mean(p['sample_size'])))) or group < (statistics.mean(p['p'])-3*(np.sqrt((statistics.mean(p['p'])*(1-statistics.mean(p['p'])))/statistics.mean(p['sample_size'])))):
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
        
    df_grouped = pd.DataFrame()
    df_grouped['x_bar']=p[1]
    df_grouped.index = np.arange(1, len(df_grouped) + 1)
    df_grouped['x_bar_bar'] = statistics.mean(p['p'])
    df_grouped['UCL'] = statistics.mean(p['p'])+3*(np.sqrt((statistics.mean(p['p'])*(1-statistics.mean(p['p'])))/(p['sample_size'])))
    df_grouped['+2s'] = statistics.mean(p['p'])+2*(np.sqrt((statistics.mean(p['p'])*(1-statistics.mean(p['p'])))/(p['sample_size'])))
    df_grouped['+1s'] = statistics.mean(p['p'])+1*(np.sqrt((statistics.mean(p['p'])*(1-statistics.mean(p['p'])))/(p['sample_size'])))
    df_grouped['-1s'] = statistics.mean(p['p'])-1*(np.sqrt((statistics.mean(p['p'])*(1-statistics.mean(p['p'])))/(p['sample_size'])))
    df_grouped['-2s'] = statistics.mean(p['p'])-2*(np.sqrt((statistics.mean(p['p'])*(1-statistics.mean(p['p'])))/(p['sample_size'])))
    df_grouped['LCL'] = statistics.mean(p['p'])-3*(np.sqrt((statistics.mean(p['p'])*(1-statistics.mean(p['p'])))/(p['sample_size'])))
    
    controlSay = detector.anomalyDetection(df_grouped)
    plt.savefig('./static/temp.png')   # save the figure to file
    figLegend = pylab.figure(figsize = (2,2))
    pylab.figlegend(*ax.get_legend_handles_labels(), loc = 'upper left')
    figLegend.savefig("./static/legend.png")
    return analysis1, analysis2, controlSay