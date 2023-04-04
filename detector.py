# importing necessay libraries
from flask import Flask, app, render_template, request, url_for, redirect, session
from fileinput import filename
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics

# main function to detect anomalies
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
