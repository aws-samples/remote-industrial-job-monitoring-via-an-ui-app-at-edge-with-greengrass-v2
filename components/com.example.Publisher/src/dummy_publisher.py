# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import time
import datetime
import json
from random import randint
import random
import awsiot.greengrasscoreipc
from awsiot.greengrasscoreipc.model import (
    PublishToTopicRequest,
    PublishMessage,
    JsonMessage
)


TIMEOUT = 100
publish_rate = 10

ipc_client = awsiot.greengrasscoreipc.connect()

# the topic name where the messages are to be published
topic = "runscreen/topic"


class IPCTopic:
    
    #function to publish the message to the topic
    def publish_to_topic(self,topic_name,message):
        request = PublishToTopicRequest()
        request.topic = topic_name
        publish_message = PublishMessage()
        publish_message.json_message = JsonMessage()
        publish_message.json_message.message = message
        request.publish_message = publish_message
        operation = ipc_client.new_publish_to_topic()
        operation.activate(request)
        future = operation.get_response()
        future.result(TIMEOUT)

    #function to generate the json message
    def generate_message(self,quality_control,tool_status,msg):
        print("generate the json messageg")
        sensor_data ={}
        operating_parameters = {}
        qualitycontrolVal = random.choice(quality_control)
        if qualitycontrolVal == 'Passed':
            operating_parameters = {
                "quality_control" : qualitycontrolVal,
                "tool_status" : tool_status[0],
                "message" : msg[0]
            }
        else:
            operating_parameters = {
                "quality_control" : qualitycontrolVal,
                "tool_status" : tool_status[0],
                "message" : msg[1]
            }            
        power_curve = "{}".format(randint(300,400))
        wind_speed = "{}".format(round(random.uniform(5, 15), 2))
        wind_direction = "{}".format(round(random.uniform(150, 300), 2))
        lv_activepower = "{}".format(round(random.uniform(200.12, 300.66), 2))
        sensor_data = {
            "power_curve":power_curve,
            "lv_activepower":lv_activepower,
            "wind_speed": wind_speed,
            "wind_direction":wind_direction
        }
    
        message = {
            "timestamp": str(datetime.datetime.now()),
            "Operating Parameters": operating_parameters,
            "Sensor Data": sensor_data
        }
        return message
        
obj_ipctopic = IPCTopic()
# declare variables
quality_control = ["Passed","Action Needed"]
tool_status = ["running","stopped"]
msg = [
    {"Job continues":
        {
            "Site Environment":"OK",
            "Recommended Action":"None"
        }
    },
    {"Restart the job":
        {
            "Site Environment":"Output is higher than threshold",
            "Recommended Action":"Monitor power output"
        }
    }
]

while True:
    
    # retrieve the json message to be published
    message = obj_ipctopic.generate_message(quality_control,tool_status,msg)
    
    # publish the message  to the topic
    obj_ipctopic.publish_to_topic(topic,message)

    # print the message generated in the logs
    message_json = json.dumps(message)
    print("The published json message is: ",message_json)
    
    time.sleep(publish_rate)
