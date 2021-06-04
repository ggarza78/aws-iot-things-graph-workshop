import time
import boto3
import json
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# This Lambda function will publish results of the read gauge function to IoT topic and SNS
# Note that this function is only used in greengrass deployment where we cannot publish directly to these services using Things Graph 

def handler(event,context):
    service = event["service"] # The Service to be sent to
    topic =  event["topic"]  # The topic the message will be sent to
    messagePayload = {}
    response = {}
    try:
        if (service == "sns"):
            messagePayload["gaugeReading"] = event["gaugeReading"]
            sendSNSMessage(topic,messagePayload)
        else :
            messagePayload["s3ObjectKey"] = event["s3ObjectKey"]
            messagePayload["s3BucketName"] = event["s3BucketName"]
            messagePayload["gaugeType"] = event["gaugeType"]
            messagePayload["gaugeID"] = event["gaugeID"]
            messagePayload["gaugeReading"] = event["gaugeReading"]
            messagePayload["timeStamp"] = event["timeStamp"]
            messagePayload["errorCode"] = event["errorCode"]
            messagePayload["errorMessage"] = event["errorMessage"]
            sendIoTMessage(topic,messagePayload)    
        response =  messagePayload
    except Exception as e: 
        logger.error('Error: {}'.format(e))
        response['errorMessage'] = e
    return response

def sendSNSMessage(topic,messagePayload):
    client = boto3.client('sns')
    response = client.publish(
    TargetArn=topic,
    Message=json.dumps({'default': json.dumps(messagePayload)}),
    MessageStructure='json'
)

def sendIoTMessage(topic,messagePayload):
    iotClient = boto3.client('iot')
    endpoint= iotClient.describe_endpoint(endpointType='iot:Data-ATS');
    endpointAddress= endpoint['endpointAddress']

    client = boto3.client('iot-data', endpoint_url='https://'+endpointAddress)
    response = client.publish(
        topic = topic,
        qos = 0,
        payload = json.dumps(messagePayload)
    )