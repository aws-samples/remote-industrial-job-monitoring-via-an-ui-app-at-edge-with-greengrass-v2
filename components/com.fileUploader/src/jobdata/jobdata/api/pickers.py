from jobdata import app
from jobdata.api import uploadFile as uf
import json
import sys
import os
from flask import request
import argparse

__all__ = ["index"]


@app.route("/")
def index():
    return "Hello World"


@app.route("/uploadfile",methods=['POST'])
def upload():
    bucketName =  app.config['s3bucket']
    
    print("in upload function")
    file=request.files['filename']
    print("the file is : ",file.filename)
    filePath = "uploadedfile"
    isExist = os.path.exists(filePath)
    if not isExist:
        # Create a new directory because it does not exist 
        os.makedirs(filePath)
        print("The new directory is created!")
    file.save(filePath+"/"+file.filename)    
    return uf.upload_json(bucketName, filePath+"/"+file.filename)