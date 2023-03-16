from flask import Flask, app, render_template, request, url_for, redirect, session
from fileinput import filename
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics
import PyQt5
import io
import random
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import urllib.request
import requests

app = Flask(__name__)
app.secret_key = "super secret key"


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/data', methods=['POST'])
def data():
    excelData = request.files['upload-file']
    df = pd.read_excel(excelData, sheet_name="set_2")
    what_type, what = boot(df)
    session["what_type"]=what_type
    session["what"]=what
    if(what=="Data will use 'X bar & R chart'"):
        analysis, controlSay, fig = xbar_r(df)
    elif(what=="Data will use 'X bar & S chart'"):
        xbar_s(df)
    elif(what=="Data will use 'XmR chart'"):
        xmR(df)
    elif(what=="Data will use 'C chart'"):
        cChart(df)
    elif(what=="Data will use 'P chart'"):
        pChart(df)
    session["analysis"]=analysis
    session['controlSay']=controlSay
    return redirect(url_for('temp'))

@app.route('/temp', methods=['POST', 'GET'])
def temp():
    what_type=session.get("what_type")
    what=session.get("what")
    analysis=session.get("analysis")
    controlSay=session.get("controlSay")     
    return {
        "what_type":what_type,
        "what":what,
        "analysis": analysis,
        "controlSay": controlSay,
    }


def boot(sample_data):
    what_type=""
    what=""
    try:
        i = 0
        num_col = len(sample_data.columns) - 1
        flag_conti = True
        while i < num_col:
            if (sample_data[i+1]%1 == 0).all():
                flag_conti = False
            i+=1
        if flag_conti:
            what_type="Data is continuous"
            ## is there more than one data per subgroup?
            flag_subgroup = False
            num_col = len(sample_data.columns) - 1
            if num_col > 1 :
                flag_subgroup = True
                if num_col > 10:
                    what="Data will use 'X bar & S chart'"
                else:
                    what="Data will use 'X bar & R chart'"
            else:
                what="Data will use 'XmR chart'"
        else:
            what_type="Data is discrete"
            ## does data follow Poisson distribution or Binomial
            flag_poisson = False
            mean = round(sample_data[1].mean(),0)
            var = round((sample_data[1].var()),0)
            if(mean == var):
                flag_poisson = True
                what="Data will use 'C chart'"
            else:
                what="Data will use 'P chart'"
    except:
        sample_size_temp = sample_data.columns.values[2]
        what_type="Data is discrete"
        what="Data will use 'P chart'"
    
    return what_type, what

def anomalyDetection(df_grouped):    
    # Control chart rules lists setup
    R1_lower = []
    R1_upper = []
    R2_lower = ['-','-']
    R2_upper = ['-','-']
    R3_lower = ['-','-','-','-']
    R3_upper = ['-','-','-','-']
    R4_lower = ['-','-','-','-','-','-']
    R4_upper = ['-','-','-','-','-','-']
    R5_down = ['-','-','-','-','-','-']
    R5_up = ['-','-','-','-','-','-']
    R6 = ['-','-','-','-','-','-','-']
    R7 = ['-','-','-','-','-','-','-','-','-','-','-','-','-','-']
    R8 = ['-','-','-','-','-','-','-','-','-','-','-','-','-']

    # Rule 1 - Lower
    for x in df_grouped['x_bar']:
        if x < df_grouped['LCL'][1]:
            R1_lower.append(False)
        else:
            R1_lower.append(True)

    # Rule 1 - Upper
    for x in df_grouped['x_bar']:
        if x > df_grouped['UCL'][1]:
            R1_upper.append(False)
        else:
            R1_upper.append(True)

    # Rule 2 - Lower
    i = 3
    while i <= len(df_grouped['x_bar']):
        if((df_grouped['x_bar'][i] < df_grouped['-2s'][i] and df_grouped['x_bar'][i-1] < df_grouped['-2s'][i-1]) or 
           (df_grouped['x_bar'][i-1] < df_grouped['-2s'][i-1] and df_grouped['x_bar'][i-2] < df_grouped['-2s'][i-2]) or
           (df_grouped['x_bar'][i] < df_grouped['-2s'][i] and df_grouped['x_bar'][i-2] < df_grouped['-2s'][i-2])):
            R2_lower.append(False)
        else:
            R2_lower.append(True)
        i+=1

    # Rule 2 - Upper
    i = 3
    while i <= len(df_grouped['x_bar']):
        if((df_grouped['x_bar'][i] > df_grouped['+2s'][i] and df_grouped['x_bar'][i-1] > df_grouped['+2s'][i-1]) or
           (df_grouped['x_bar'][i-1] > df_grouped['+2s'][i-1] and df_grouped['x_bar'][i-2] > df_grouped['+2s'][i-2]) or
           (df_grouped['x_bar'][i] > df_grouped['+2s'][i] and df_grouped['x_bar'][i-2] > df_grouped['+2s'][i-2])):
            R2_upper.append(False)
        else:
            R2_upper.append(True)
        i+=1

    # Rule 3 - Lower
    i = 5
    while i <= len(df_grouped['x_bar']):
        if((df_grouped['x_bar'][i-4] < df_grouped['-1s'][i-4] and df_grouped['x_bar'][i-3] < df_grouped['-1s'][i-3] and df_grouped['x_bar'][i-2] < df_grouped['-1s'][i-2] and df_grouped['x_bar'][i-1] < df_grouped['-1s'][i-1]) or
           (df_grouped['x_bar'][i-4] < df_grouped['-1s'][i-4] and df_grouped['x_bar'][i-3] < df_grouped['-1s'][i-3] and df_grouped['x_bar'][i-2] < df_grouped['-1s'][i-2] and df_grouped['x_bar'][i] < df_grouped['-1s'][i]) or
           (df_grouped['x_bar'][i-4] < df_grouped['-1s'][i-4] and df_grouped['x_bar'][i-2] < df_grouped['-1s'][i-2] and df_grouped['x_bar'][i-1] < df_grouped['-1s'][i-1] and df_grouped['x_bar'][i] < df_grouped['-1s'][i]) or
           (df_grouped['x_bar'][i-4] < df_grouped['-1s'][i-4] and df_grouped['x_bar'][i-3] < df_grouped['-1s'][i-3] and df_grouped['x_bar'][i-1] < df_grouped['-1s'][i-1] and df_grouped['x_bar'][i] < df_grouped['-1s'][i]) or
           (df_grouped['x_bar'][i-3] < df_grouped['-1s'][i-3] and df_grouped['x_bar'][i-2] < df_grouped['-1s'][i-2] and df_grouped['x_bar'][i-1] < df_grouped['-1s'][i-1] and df_grouped['x_bar'][i] < df_grouped['-1s'][i])):
            R3_lower.append(False)
        else:
            R3_lower.append(True)
        i+=1

    # Rule 3 - Upper
    i = 5
    while i <= len(df_grouped['x_bar']):
        if((df_grouped['x_bar'][i-4] > df_grouped['+1s'][i-4] and df_grouped['x_bar'][i-3] > df_grouped['+1s'][i-3] and df_grouped['x_bar'][i-2] > df_grouped['+1s'][i-2] and df_grouped['x_bar'][i-1] > df_grouped['+1s'][i-1]) or
           (df_grouped['x_bar'][i-4] > df_grouped['+1s'][i-4] and df_grouped['x_bar'][i-3] > df_grouped['+1s'][i-3] and df_grouped['x_bar'][i-2] > df_grouped['+1s'][i-2] and df_grouped['x_bar'][i] > df_grouped['+1s'][i]) or
           (df_grouped['x_bar'][i-4] > df_grouped['+1s'][i-4] and df_grouped['x_bar'][i-2] > df_grouped['+1s'][i-2] and df_grouped['x_bar'][i-1] > df_grouped['+1s'][i-1] and df_grouped['x_bar'][i] > df_grouped['+1s'][i]) or
           (df_grouped['x_bar'][i-4] > df_grouped['+1s'][i-4] and df_grouped['x_bar'][i-3] > df_grouped['+1s'][i-3] and df_grouped['x_bar'][i-1] > df_grouped['+1s'][i-1] and df_grouped['x_bar'][i] > df_grouped['+1s'][i]) or
           (df_grouped['x_bar'][i-3] > df_grouped['+1s'][i-3] and df_grouped['x_bar'][i-2] > df_grouped['+1s'][i-2] and df_grouped['x_bar'][i-1] > df_grouped['+1s'][i-1] and df_grouped['x_bar'][i] > df_grouped['+1s'][i])):
            R3_upper.append(False)
        else:
            R3_upper.append(True)
        i+=1

    # Rule 4 - Lower
    i = 7
    while i <= len(df_grouped['x_bar']):
        if(df_grouped['x_bar'][i] < df_grouped['x_bar_bar'][i] and
           df_grouped['x_bar'][i-1] < df_grouped['x_bar_bar'][i-1] and
           df_grouped['x_bar'][i-2] < df_grouped['x_bar_bar'][i-2] and
           df_grouped['x_bar'][i-3] < df_grouped['x_bar_bar'][i-3] and
           df_grouped['x_bar'][i-4] < df_grouped['x_bar_bar'][i-4] and
           df_grouped['x_bar'][i-5] < df_grouped['x_bar_bar'][i-5] and
           df_grouped['x_bar'][i-6] < df_grouped['x_bar_bar'][i-6]):
            R4_lower.append(False)
        else:
            R4_lower.append(True)
        i+=1

    # Rule 4 - Upper
    i = 7
    while i <= len(df_grouped['x_bar']):
        if(df_grouped['x_bar'][i] > df_grouped['x_bar_bar'][i] and
           df_grouped['x_bar'][i-1] > df_grouped['x_bar_bar'][i-1] and
           df_grouped['x_bar'][i-2] > df_grouped['x_bar_bar'][i-2] and
           df_grouped['x_bar'][i-3] > df_grouped['x_bar_bar'][i-3] and
           df_grouped['x_bar'][i-4] > df_grouped['x_bar_bar'][i-4] and
           df_grouped['x_bar'][i-5] > df_grouped['x_bar_bar'][i-5] and
           df_grouped['x_bar'][i-6] > df_grouped['x_bar_bar'][i-6]):
            R4_upper.append(False)
        else:
            R4_upper.append(True)
        i+=1

    # Rule 5 - Trend Down
    i = 7
    while i <= len(df_grouped['x_bar']):
        if(df_grouped['x_bar'][i] < df_grouped['x_bar'][i-1] and
          df_grouped['x_bar'][i-1] < df_grouped['x_bar'][i-2] and
          df_grouped['x_bar'][i-2] < df_grouped['x_bar'][i-3] and
          df_grouped['x_bar'][i-3] < df_grouped['x_bar'][i-4] and
          df_grouped['x_bar'][i-4] < df_grouped['x_bar'][i-5] and
          df_grouped['x_bar'][i-5] < df_grouped['x_bar'][i-6]):
            R5_down.append(False)
        else:
            R5_down.append(True)
        i+=1

    # Rule 5 - Trend Up
    i = 7
    while i <= len(df_grouped['x_bar']):
        if(df_grouped['x_bar'][i] > df_grouped['x_bar'][i-1] and
          df_grouped['x_bar'][i-1] > df_grouped['x_bar'][i-2] and
          df_grouped['x_bar'][i-2] > df_grouped['x_bar'][i-3] and
          df_grouped['x_bar'][i-3] > df_grouped['x_bar'][i-4] and
          df_grouped['x_bar'][i-4] > df_grouped['x_bar'][i-5] and
          df_grouped['x_bar'][i-5] > df_grouped['x_bar'][i-6]):
            R5_up.append(False)
        else:
            R5_up.append(True)
        i+=1

    # Rule 6
    i = 8
    while i <= len(df_grouped['x_bar']):
        if((df_grouped['x_bar'][i] < df_grouped['-1s'][i] or df_grouped['x_bar'][i] > df_grouped['+1s'][i]) and
           (df_grouped['x_bar'][i-1] < df_grouped['-1s'][i-1] or df_grouped['x_bar'][i-1] > df_grouped['+1s'][i-1]) and
           (df_grouped['x_bar'][i-2] < df_grouped['-1s'][i-2] or df_grouped['x_bar'][i-2] > df_grouped['+1s'][i-2]) and
           (df_grouped['x_bar'][i-3] < df_grouped['-1s'][i-3] or df_grouped['x_bar'][i-3] > df_grouped['+1s'][i-3]) and
           (df_grouped['x_bar'][i-4] < df_grouped['-1s'][i-4] or df_grouped['x_bar'][i-4] > df_grouped['+1s'][i-4]) and
           (df_grouped['x_bar'][i-5] < df_grouped['-1s'][i-5] or df_grouped['x_bar'][i-5] > df_grouped['+1s'][i-5]) and
           (df_grouped['x_bar'][i-6] < df_grouped['-1s'][i-6] or df_grouped['x_bar'][i-6] > df_grouped['+1s'][i-6]) and
           (df_grouped['x_bar'][i-7] < df_grouped['-1s'][i-7] or df_grouped['x_bar'][i-7] > df_grouped['+1s'][i-7])):
            R6.append(False)
        else:
            R6.append(True)
        i+=1

    # Rule 7
    i = 15
    while i <= len(df_grouped['x_bar']):
        if(((df_grouped['x_bar'][i] < df_grouped['x_bar_bar'][i] and df_grouped['x_bar'][i] > df_grouped['-1s'][i]) or (df_grouped['x_bar'][i] > df_grouped['x_bar_bar'][i] and df_grouped['x_bar'][i] < df_grouped['+1s'][i])) and
           ((df_grouped['x_bar'][i-1] < df_grouped['x_bar_bar'][i-1] and df_grouped['x_bar'][i-1] > df_grouped['-1s'][i-1]) or (df_grouped['x_bar'][i-1] > df_grouped['x_bar_bar'][i-1] and df_grouped['x_bar'][i-1] < df_grouped['+1s'][i-1])) and
           ((df_grouped['x_bar'][i-2] < df_grouped['x_bar_bar'][i-2] and df_grouped['x_bar'][i-2] > df_grouped['-1s'][i-2]) or (df_grouped['x_bar'][i-2] > df_grouped['x_bar_bar'][i-2] and df_grouped['x_bar'][i-2] < df_grouped['+1s'][i-2])) and
           ((df_grouped['x_bar'][i-3] < df_grouped['x_bar_bar'][i-3] and df_grouped['x_bar'][i-3] > df_grouped['-1s'][i-3]) or (df_grouped['x_bar'][i-3] > df_grouped['x_bar_bar'][i-3] and df_grouped['x_bar'][i-3] < df_grouped['+1s'][i-3])) and
           ((df_grouped['x_bar'][i-4] < df_grouped['x_bar_bar'][i-4] and df_grouped['x_bar'][i-4] > df_grouped['-1s'][i-4]) or (df_grouped['x_bar'][i-4] > df_grouped['x_bar_bar'][i-4] and df_grouped['x_bar'][i-4] < df_grouped['+1s'][i-4])) and
           ((df_grouped['x_bar'][i-5] < df_grouped['x_bar_bar'][i-5] and df_grouped['x_bar'][i-5] > df_grouped['-1s'][i-5]) or (df_grouped['x_bar'][i-5] > df_grouped['x_bar_bar'][i-5] and df_grouped['x_bar'][i-5] < df_grouped['+1s'][i-5])) and
           ((df_grouped['x_bar'][i-6] < df_grouped['x_bar_bar'][i-6] and df_grouped['x_bar'][i-6] > df_grouped['-1s'][i-6]) or (df_grouped['x_bar'][i-6] > df_grouped['x_bar_bar'][i-6] and df_grouped['x_bar'][i-6] < df_grouped['+1s'][i-6])) and
           ((df_grouped['x_bar'][i-7] < df_grouped['x_bar_bar'][i-7] and df_grouped['x_bar'][i-7] > df_grouped['-1s'][i-7]) or (df_grouped['x_bar'][i-7] > df_grouped['x_bar_bar'][i-7] and df_grouped['x_bar'][i-7] < df_grouped['+1s'][i-7])) and
           ((df_grouped['x_bar'][i-8] < df_grouped['x_bar_bar'][i-8] and df_grouped['x_bar'][i-8] > df_grouped['-1s'][i-8]) or (df_grouped['x_bar'][i-8] > df_grouped['x_bar_bar'][i-8] and df_grouped['x_bar'][i-8] < df_grouped['+1s'][i-8])) and
           ((df_grouped['x_bar'][i-9] < df_grouped['x_bar_bar'][i-9] and df_grouped['x_bar'][i-9] > df_grouped['-1s'][i-9]) or (df_grouped['x_bar'][i-9] > df_grouped['x_bar_bar'][i-9] and df_grouped['x_bar'][i-9] < df_grouped['+1s'][i-9])) and
           ((df_grouped['x_bar'][i-10] < df_grouped['x_bar_bar'][i-10] and df_grouped['x_bar'][i-10] > df_grouped['-1s'][i-10]) or (df_grouped['x_bar'][i-10] > df_grouped['x_bar_bar'][i-10] and df_grouped['x_bar'][i-10] < df_grouped['+1s'][i-10])) and
           ((df_grouped['x_bar'][i-11] < df_grouped['x_bar_bar'][i-11] and df_grouped['x_bar'][i-11] > df_grouped['-1s'][i-11]) or (df_grouped['x_bar'][i-11] > df_grouped['x_bar_bar'][i-11] and df_grouped['x_bar'][i-11] < df_grouped['+1s'][i-11])) and
           ((df_grouped['x_bar'][i-12] < df_grouped['x_bar_bar'][i-12] and df_grouped['x_bar'][i-12] > df_grouped['-1s'][i-12]) or (df_grouped['x_bar'][i-12] > df_grouped['x_bar_bar'][i-12] and df_grouped['x_bar'][i-12] < df_grouped['+1s'][i-12])) and
           ((df_grouped['x_bar'][i-13] < df_grouped['x_bar_bar'][i-13] and df_grouped['x_bar'][i-13] > df_grouped['-1s'][i-13]) or (df_grouped['x_bar'][i-13] > df_grouped['x_bar_bar'][i-13] and df_grouped['x_bar'][i-13] < df_grouped['+1s'][i-13])) and
           ((df_grouped['x_bar'][i-14] < df_grouped['x_bar_bar'][i-14] and df_grouped['x_bar'][i-14] > df_grouped['-1s'][i-14]) or (df_grouped['x_bar'][i-14] > df_grouped['x_bar_bar'][i-14] and df_grouped['x_bar'][i-14] < df_grouped['+1s'][i-14]))):
            R7.append(False)
        else:
            R7.append(True)
        i+=1

    # Rule #8
    i = 14
    while i <= len(df_grouped['x_bar']):
        if(((df_grouped['x_bar'][i] > df_grouped['x_bar'][i-1]) and
           (df_grouped['x_bar'][i-1] < df_grouped['x_bar'][i-2]) and
           (df_grouped['x_bar'][i-2] > df_grouped['x_bar'][i-3]) and
           (df_grouped['x_bar'][i-3] < df_grouped['x_bar'][i-4]) and
           (df_grouped['x_bar'][i-4] > df_grouped['x_bar'][i-5]) and
           (df_grouped['x_bar'][i-5] < df_grouped['x_bar'][i-6]) and
           (df_grouped['x_bar'][i-6] > df_grouped['x_bar'][i-7]) and
           (df_grouped['x_bar'][i-7] < df_grouped['x_bar'][i-8]) and
           (df_grouped['x_bar'][i-8] > df_grouped['x_bar'][i-9]) and
           (df_grouped['x_bar'][i-9] < df_grouped['x_bar'][i-10]) and
           (df_grouped['x_bar'][i-10] > df_grouped['x_bar'][i-11]) and
           (df_grouped['x_bar'][i-11] < df_grouped['x_bar'][i-12]) and
           (df_grouped['x_bar'][i-12] > df_grouped['x_bar'][i-13])) or
           ((df_grouped['x_bar'][i] < df_grouped['x_bar'][i-1]) and
           (df_grouped['x_bar'][i-1] > df_grouped['x_bar'][i-2]) and
           (df_grouped['x_bar'][i-2] < df_grouped['x_bar'][i-3]) and
           (df_grouped['x_bar'][i-3] > df_grouped['x_bar'][i-4]) and
           (df_grouped['x_bar'][i-4] < df_grouped['x_bar'][i-5]) and
           (df_grouped['x_bar'][i-5] > df_grouped['x_bar'][i-6]) and
           (df_grouped['x_bar'][i-6] < df_grouped['x_bar'][i-7]) and
           (df_grouped['x_bar'][i-7] > df_grouped['x_bar'][i-8]) and
           (df_grouped['x_bar'][i-8] < df_grouped['x_bar'][i-9]) and
           (df_grouped['x_bar'][i-9] > df_grouped['x_bar'][i-10]) and
           (df_grouped['x_bar'][i-10] < df_grouped['x_bar'][i-11]) and
           (df_grouped['x_bar'][i-11] > df_grouped['x_bar'][i-12]) and
           (df_grouped['x_bar'][i-12] < df_grouped['x_bar'][i-13]))):
            R8.append(False)
        else:
            R8.append(True)
        i+=1

    # Define outcomes data frame
    analysis = pd.DataFrame({'R1_lower':R1_lower,
                            'R1_upper':R1_upper,
                            'R2_lower':R2_lower,
                            'R2_upper':R2_upper,
                            'R3_lower':R3_lower,
                            'R3_upper':R3_upper,
                            'R4_lower':R4_lower,
                            'R4_upper':R4_upper,
                            'R5_down':R5_down,
                            'R5_up':R5_up,
                            'R6':R6,
                            'R7':R7,
                            'R8':R8})
    analysis.index = df_grouped.index

    # Look for at least one False value in each of the control chart rules
    what=""
    control_check=True
    for x in analysis.all() :
        if x==False :
            control_check=False
            break
    if control_check==True :
        what="Process is in Control"
    else :
        what="Process is Out of Control"
    
    return what

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
    controlSay = anomalyDetection(df_grouped)
    return analysis, controlSay, fig

def xbar_s(sample_data):
    return "working"

def xmR(sample_data):
    return "working"

def cChart(sample_data):
    return "working"

def pChart(sample_data):
    return "working"
