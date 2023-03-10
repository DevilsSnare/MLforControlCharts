from flask import Flask, app, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')

@app.route('/get_csv_data', methods = ['POST'])
def get_csv_data():
    jsdata = request.form['csv_data']
    print (jsdata)
    return jsdata

