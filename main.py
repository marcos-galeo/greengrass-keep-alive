import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
import sys
from awsiot.greengrasscoreipc.model import (
    QOS,
    PublishToIoTCoreRequest,
    IoTCoreMessage,
    SubscribeToIoTCoreRequest
)
import time
import json
from src.configuration import Configuration


TIMEOUT = 10
DELAY = int(sys.argv[1])
ipc_client = awsiot.greengrasscoreipc.connect()

topic = '/telemetry/alive/timer'
qos = QOS.AT_LEAST_ONCE
conf = Configuration(DELAY)


def updateDelay(delay):
    conf.delay = delay

class StreamHandler(client.SubscribeToIoTCoreStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: IoTCoreMessage) -> None:
        try:
            message = str(event.message.payload, "utf-8")
            topic_name = event.message.topic_name
            message_dictionary = json.loads(message)
            print(message_dictionary.keys())
            if "delay" in message_dictionary.keys():
                new_delay = int(message_dictionary["delay"])
                print("There is a new delay of: {}".format(new_delay))
                updateDelay(new_delay)
            #else:
            #    print(message)
        except:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        # Handle error.
        return True  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        # Handle close.
        pass

print("Starting Subscribe Request")
subscribe_request = SubscribeToIoTCoreRequest()
subscribe_request.topic_name = topic
subscribe_request.qos = qos
handler = StreamHandler()
operation = ipc_client.new_subscribe_to_iot_core(handler)
future = operation.activate(subscribe_request)
future.result(TIMEOUT)
print("Subscriber activated")

publish_topic = "telemetry/alive"
publish_message = "I'm alive"
print("Delayed time every: {} seconds".format(conf.delay))
while True:
    request = PublishToIoTCoreRequest()
    request.topic_name = publish_topic
    request.payload = bytes(json.dumps({"message":publish_message,"current delay:":conf.delay}), "utf-8")
    request.qos = qos
    operation = ipc_client.new_publish_to_iot_core()
    operation.activate(request)
    print("Sending {} to topic: {}".format(publish_message,publish_topic))
    future = operation.get_response()
    future.result(TIMEOUT)
    print("Sent {} to topic: {}".format(publish_message,publish_topic))
    time.sleep(conf.delay)