from flask import Flask,request,jsonify,flash,session
from flask_restful import Api
from flask_cors import CORS,cross_origin
import tempfile
import os
import tika
import regex as re
tika.initVM()
from tika import parser



app = Flask(__name__)
CORS(app)
CORS(app, intercept_exceptions=False)
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
@cross_origin()
def upload_file():
    output=""
    try:
        print("lol")
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
        file = request.files['file']
        print(file)
        # if usgiter does not select file, browser also
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
        
        print("check if text is returned")

    return output
    print(file)
if __name__ == '__main__':
    app.run(debug=True)
