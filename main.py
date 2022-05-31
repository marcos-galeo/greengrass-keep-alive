import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
import sys
from awsiot.greengrasscoreipc.model import (
    QOS,
    PublishToIoTCoreRequest
)

TIMEOUT = 10

ipc_client = awsiot.greengrasscoreipc.connect()
                    
topic = "my/topic"
message = "Hello, World"
qos = QOS.AT_LEAST_ONCE
request = PublishToIoTCoreRequest()
request.topic_name = topic
request.payload = bytes(message, "utf-8")
request.qos = qos
operation = ipc_client.new_publish_to_iot_core()
operation.activate(request)
print("Sending {} to topic: {}".format(message,topic))
future = operation.get_response()
future.result(TIMEOUT)
print("Sent {} to topic: {}".format(message,topic))
