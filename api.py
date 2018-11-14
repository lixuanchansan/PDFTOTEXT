from flask import Flask,request,jsonify,flash,session
from flask_restful import Api
from flask_cors import CORS,cross_origin
import tempfile
import os
import tika
import regex as re
tika.initVM()
from tika import parser
import requests
from bs4 import BeautifulSoup
import pickle
from urllib.request import urlopen



app = Flask(__name__)
app.secret_key = "super secret key"
CORS(app)

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
    print(repr(file))
    return clean_space_tab(output)

def clean_space_tab(text):
    text = re.sub(r'[ ]{2,}',' ', text) #Replaces x multiple of space with 1 space
    text = re.sub("\t+",' ', text) #Replaces x multiple of tab with 1 space
    #text = re.sub( '\s+', ' ', text ).strip()
    return text


###################### DATA CLEANING #############################

# removing text file headers, footers
# removing HTML, XML, etc. markup and metadata

def strip_html(text):
    soup = BeautifulSoup(text, "html.parser") #WORKS
    return soup.get_text()

def remove_bet_pointy_braces(text):
    return re.sub('<.*?>', '', text) #WORKS

def remove_between_square_brackets(text):
    return re.sub('\[[^]]*\]', '', text) #WORKS

def remove_surrounding_colon_http_chat(text) : 
     # output = re.sub('\w\w*\:\w\w*','HEY FIRVE ', text) # DONE 00: not so accurate 3
     # output = re.sub('\w\w*\:\w\w*','    ONE  ', text) # REMOVES 00:00 more tamed version 2
    #return re.sub('\w\w*\:.*?\s+',' ', text) #removes https, http, and anything revolving : 1
    text = re.sub(r'http\S+', '', text)
    return re.sub('\w+\w*\:+.*?',' ', text)
    #https to end documentation
    # output = re.sub('https.*?\s+', '', text) #doesnt work solved above
    # output = re.sub('http.*?\s+', '', text) #doesnt work solved above
    # output = re.sub('www.*?\s+', '', text) #doesnt work solved above

def remove_surroundinghash(text) :
    text = re.sub(r'#\S+', '', text)
    text = re.sub(r'#\d+', '', text)
    return re.sub('\w\w*\#.*?\s+',' ',text) #removes "hi#kubuntu-devel- "" 1 
    # output = re.sub('\#.*?\s+',' ',text) #removes "hi#kubuntu-devel 2
   # output = re.sub('\B(\#[a-zA-Z]+b)(?!;)','DONE FOUR', text) #doesnt work bad perf 3

def remove_equals(text) :
    return  re.sub('=', ' ', text)

def remove_backslash(text) :
    return  re.sub('\"', ' ', text)

def clean_you(text):

# clean -<word>- --> with a space in between? like  -kubuntu- 
    output = re.sub(r'(?<![a-z])u(?![a-z])', 'you', text, flags=re.I) #WORKS, changes 'U' and 'u' to 'you'
    
    output = re.sub(r'( -\b)',' ', output) #Removes - from front of strings (unless it is first character in text file)
    output = re.sub(r'(\b- )',' ', output) #Removes - from back of strings (Except if it is the last character in the file)
   
    #output = re.sub(r'(\b-)','', output) 
    #output = re.sub(r'(-\b)','', output) 
    #output = re.sub(r'(?<![a-z])-','', output) 
    #output = re.sub(r'\b- ',' ', output) 
    return output

def clean_space_tab(text):
    text = re.sub(r'[ ]{2,}',' ', text) #Replaces x multiple of space with 1 space
    text = re.sub("\t+",' ', text) #Replaces x multiple of tab with 1 space
    #return text
    return text.replace("\s+|^[ \t]+|[ \t]+$"," ")

def denoise_text(text):
    num_chars_before = len(text.replace(" ", "")) #Count length of each line without whitespace
    print("Characters before cleaning:", num_chars_before)  
    #text = remove_between_square_brackets(text) #DONE
    #text = remove_bet_pointy_braces(text) #DONE
    #text = remove_surroundinghash(text) #DONE
    #text = remove_surrounding_colon_http_chat(text) #DONE
    #text = clean_you(text)  #TO_DO_1 EUGENE
    #Also, 2. replace #, 3.  -kubuntu- // words bet 2 "-"  
    #text = remove_equals(text) #DONE
    #text =  remove_backslash(text)  #DONE
    text = strip_html(text) #DONE
    #text = clean_space_tab(text)
    num_chars_after = len(text.replace(" ", "")) #Count length of each line without whitespace    
    print("Characters after cleaning:", num_chars_after)
    return text
    

@app.route('/scrap', methods=['POST'])
def scraping():
    data = request.get_json(force=True)
    url = data["url"]
    tag = data["tag"]
    print(url,tag)
    response = requests.get(url)
    print(response ,"hey")

    html_soup = BeautifulSoup(response.text, 'html.parser')
    containers = html_soup.findAll(tag)
    
    
    return denoise_text(str(containers)) 

if __name__ == '__main__':
    app.run(debug=True)
