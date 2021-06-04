#
# This Lambda function is triggered by an S3 event whenever a new image is uploaded to the bucket
# It will insert an SQS record with image data
# It will also publish a message to an IoT topic to trigger our Things Graph Flow
#

import json
import boto3
import os
import time
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    responseData = {}
    try:
        response = {}
        bucketName = event['Records'][0]['s3']['bucket']['name']
        objectKey = event['Records'][0]['s3']['object']['key']
        objectUrl = "url"
        response["bucketName"] = bucketName
        response["objectKey"] = objectKey
        response["objectUrl"] = objectUrl
        response["snsTopicArn"] = os.environ['SNS_TOPIC_ARN']
        insertRecordIntoSqs(response)
        time.sleep(20) #Sleep for 10 seconds giving the SQS message the chance to become readable
        publishToIoTTopic(response)
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    except Exception as e:
        logger.error('Error: {}'.format(e)) 
        print(e)


def insertRecordIntoSqs(payloadBody):
    sqs = boto3.client('sqs')
    queue_url = os.environ['SQS_QUEUE_URL']
    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=1,
        MessageAttributes={
            'bucketName': {
                'DataType': 'String',
                'StringValue': payloadBody['bucketName']
            },
            'objectKey': {
                'DataType': 'String',
                'StringValue': payloadBody['objectKey']
            },
            'objectUrl': {
                'DataType': 'String',
                'StringValue': payloadBody['objectUrl']
            }
        },
        MessageBody=(
            json.dumps(payloadBody)
        )
    )
    return response


def publishToIoTTopic(payloadBody):
    topicName = os.environ['IOT_TOPIC']
    iotClient = boto3.client('iot')
    endpoint= iotClient.describe_endpoint(endpointType='iot:Data-ATS');
    endpointAddress= endpoint['endpointAddress']

    client = boto3.client('iot-data', endpoint_url='https://'+endpointAddress)
    response = client.publish(
        topic = topicName,
        qos = 0,
        payload = json.dumps(payloadBody)
    )
    return response
