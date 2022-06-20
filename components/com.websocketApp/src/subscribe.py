import queue
import os
import traceback
import time
import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    SubscribeToTopicRequest,
    SubscriptionResponseMessage
)
from awscrt.io import (
    ClientBootstrap,
    DefaultHostResolver,
    EventLoopGroup,
    SocketDomain,
    SocketOptions,
)
from awsiot.eventstreamrpc import Connection, LifecycleHandler, MessageAmendment
import logging

#logging.config.fileConfig(fname='config/log.conf', disable_existing_loggers=False)
# Config the logger.
filePath = "tmp"
if not os.path.exists(filePath):
    os.makedirs(filePath)    
logging.basicConfig(filename="tmp/newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

TIMEOUT = 100

class StreamHandler(client.SubscribeToTopicStreamHandler):
    def __init__(self,lshq):
        super().__init__()
        self.shq =  lshq

    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
        logger.info("Message from IPC recevied at : {}".format(time.time()))
        try:
            message_string = str(event.json_message.message)
            with open('/tmp/websocket_Subscriber.log', 'a') as f:
                print(message_string, file=f)
            self.shq.put(message_string)
            logger.debug("Message sent to queue at : {}".format(time.time()))
        except Exception as e:
            logger.error("Exception - Failed during reading message from event - {}".format(e))          
            
    def on_stream_error(self, error: Exception) -> bool:
        print("Stream error")
        return True

    def on_stream_closed(self) -> None:
        logger.debug("Close the stream")
        pass

class MySubscriber:
    def __init__(self, lq):
        self.subq = lq

    def subscribe(self, ipc_client,topicname):
        request = SubscribeToTopicRequest()
        request.topic = topicname
        handler = StreamHandler(self.subq)
        operation = ipc_client.new_subscribe_to_topic(handler)
        future = operation.activate(request)
        #future.result(TIMEOUT)

