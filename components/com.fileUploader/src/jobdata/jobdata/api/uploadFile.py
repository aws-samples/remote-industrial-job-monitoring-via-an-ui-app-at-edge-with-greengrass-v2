import json
import logging
import sys
import os
from jobdata.api.stream_manager_s3 import sendtoS3


filePath = "logs"
isExist = os.path.exists(filePath)
if not isExist:
    # Create a new directory because it does not exist 
    os.makedirs(filePath)
    print("The new directory is created!")
logging.basicConfig(filename="logs/uploadFile.log",
                    format='%(asctime)s %(message)s',
                    filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
def upload_json(bucketname,filename):
    #read from new file
    f = open(filename, "r")
    content = f.read()
    json_data = json.loads(content)
    logger.info("the json data is : {}".format(str(json_data)))
    data ={
        "message" : "File successfully uploaded to S3"
    }
    logger.info("calling sendtoS3() to send file to S3 stream manager for the file url -  {}".format(filename))
    sendtoS3(bucketname, filename)
    logger.info("After sendtoS3()")
    return json.dumps(data)