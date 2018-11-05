from flask import Flask,request,jsonify,flash,session
from flask_restful import Api

import tempfile
import os
import tika
import regex as re
tika.initVM()
from tika import parser



app = Flask(__name__)
app.secret_key = "super secret key"


print("Start api fie")

@app.route("/")
def hello():
    return "Hello World!"
UPLOAD_FOLDER = './dump/'   
ALLOWED_EXTENSIONS = set([ 'pdf'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/pdftotext', methods=['POST'])
def upload_file():
    try:
        print("lol")
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
        file = request.files['file']
        # if user does not select file, browser also
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], "data.pdf"))

    except: 
        output="error"
        print("check if saved")

    try:
        parsed = parser.from_file('./dump/data.pdf')
        print(parsed["metadata"])
        print(parsed["content"])
        output = parsed["content"]
        output = output.replace("\r","")
        output = output.replace("\n","")
        output=output.replace("\s+|^[ \t]+|[ \t]+$"," ")
    except: 
        output= parsed["metadata"] 
        print("check if text is returned")

    return output

if __name__ == '__main__':
    app.run(debug=True)
