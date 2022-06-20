# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import time
import json
import os
import asyncio
from aiohttp import web
import socketio
import logging
import queue
import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from subscribe import MySubscriber
import sys

sio = socketio.AsyncServer(async_mode='aiohttp',cors_allowed_origins='*',logger=True, engineio_logger=True,ping_interval=20000,ping_timeout=60000)
#Create and configure logger
filePath = "codeOutput/logs"
isExist = os.path.exists(filePath)
if not isExist:
    # Create a new directory because it does not exist
    os.makedirs(filePath)
    print("The new directory is created!")
logging.basicConfig(filename="codeOutput/logs/websocket_app.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info("sio created :{} ".format(sio))
app = web.Application()
sio.attach(app)
TIMEOUT = 50

q = queue.Queue()

# Topics to subscribe
topic_run_screen = "runscreen/topic"
ipc_client = awsiot.greengrasscoreipc.connect()

#### function to subscribe to the topic, retrieve data from the topic and publish it to the front end
async def serve(sio,sid,q):
    sub_runscreen = MySubscriber(q)
    logger.debug("Initiating ipc connection")
    ipc_client = awsiot.greengrasscoreipc.connect()
    sub_runscreen.subscribe(ipc_client,topic_run_screen)
    while True:
        try:
            await sio.sleep(1)
            payload = q.get()
            msg_json = str(payload)
            logger.info("In try block  - Queue size is {}".format(q.qsize()))
            logger.info("Message was read from queue at : {}".format(time.time()))
            logger.info("the message is : {}".format(msg_json))
            await sio.emit('ipc_response',{'data':msg_json},room=sid)
            print("Message sent to socket at : {}".format(time.time()))
            #time.sleep(1)
        except Exception as e:
            print("encountered an exception -  {}".format(e))
            # This exception can happen when a client does not properly close
            # the websocket's connection, but it is irrelevant
    return

async def index(request):
    with open('/tmp/app.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

@sio.event
async def my_event(sid, message):
    await sio.emit('my_response', {'data': message['data']}, room=sid)


#### function to serve the frontend with runscreen data
@sio.event
async def publish_msg(sid,message):
    try:
        logger.info("In publish_msg")
        await serve(sio,sid,q)
    except Exception as e:
        logger.info("An exception occured in publish_msg()! - {}".format(e))


@sio.event
async def disconnect_request(sid):
    await sio.disconnect(sid)


@sio.event
async def connect(sid, environ):
    await sio.emit('my_response', {'data': 'Connected', 'count': 0}, room=sid)

@sio.event
def disconnect(sid):
    print('Client disconnected')
    logger.info("In disconnect - Client disconnected")


#app.router.add_static('/static', 'static')
app.router.add_get('/', index)

if __name__ == '__main__':
    print("starting the server")
    logger.info("starting the server")
    start_server = web.run_app(app)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
    