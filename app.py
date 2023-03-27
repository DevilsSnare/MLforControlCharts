from flask import Flask, app, render_template, request, url_for, redirect, session
from fileinput import filename
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pdftables_api
import os

import xbar_r
import xbar_s
import xmR
import cChart
import pChart
import model

app = Flask(__name__)
app.secret_key = "super secret key"

pdftables_api_key = 'ig8zw5vdtvsl'


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/data', methods=['POST'])
def data():
    excelData = request.files['upload-file']
    fname = excelData.filename[-4:]
    if fname==".pdf":
        c = pdftables_api.Client(pdftables_api_key)
        excelData.save('./static/input.pdf')
        c.xlsx('./static/input.pdf', './static/output.xlsx')
        df = pd.read_excel('./static/output.xlsx')
    else:
        df = pd.read_excel(excelData)
    
    what_type, what = boot(df)
    session["what_type"]=what_type
    session["what"]=what
    if(what=="Data will use 'X bar & R chart'"):
        analysis1, analysis2, controlSay = xbar_r.xbar_r(df)
    if(what=="Data will use 'X bar & S chart'"):
        analysis1, analysis2, controlSay = xbar_s.xbar_s(df)
    if(what=="Data will use 'C chart'"):
        analysis1, analysis2, controlSay = cChart.cChart(df)
    if(what=="Data will use 'XmR chart'"):
        analysis1, analysis2, controlSay = xmR.xmR(df)
    if(what=="Data will use 'P chart'"):
        analysis1, analysis2, controlSay = pChart.pChart(df)

    trend = model.findTrend(df)

    session['analysis1']=analysis1
    session['analysis2']=analysis2
    session['controlSay']=controlSay
    session['trend']=trend

    # os.remove('./static/input.pdf')
    # os.remove('./static/output.xlsx')

    return redirect(url_for('temp'))

@app.route('/temp', methods=['POST', 'GET'])
def temp():
    what_type=session.get("what_type")
    what=session.get("what")
    analysis1=session.get("analysis1")
    analysis2=session.get("analysis2")
    controlSay=session.get("controlSay") 
    trend=session.get("trend")    
    return {
        "what_type":what_type,
        "what":what,
        "analysis1": analysis1,
        "analysis2": analysis2,
        "controlSay": controlSay,
        "trend": trend
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
            flag_poisson = False
            mean = round(sample_data[1].mean(),0)
            var = round((sample_data[1].var()),0)
            if(mean == var):
                flag_poisson = True
                what="Data will use 'C chart'"
            else:
                what="Data will use 'C chart'"
    except:
        sample_size_temp = sample_data.columns.values[2]
        what_type="Data is discrete"
        what="Data will use 'P chart'"
    
    return what_type, what
