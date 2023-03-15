from flask import Flask, app, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route("/")
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/data', methods = ['POST'])
def data():
    excelData = request.files['upload-file']
    df = pd.read_excel(excelData)
    print(df)
    return "success"

# if __name__ == "__main__":
#     app.run(debug=True)

