'''
This function is responsible for converting the sqs payload into something that can be consumed by ThingsGraph
'''

import boto3
import json
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event,context):
    response = {'s3BucketName':'','s3ObjectKey':'','s3ObjectUrl':'','snsTopicArn':'','receiptHandle':'','errorCode':500,'errorMessage':''}
    try:
        sqsPayload = event["sqsPayload"]
        logger.info('Recieved SQS payload of: {}'.format(sqsPayload))
        body = json.loads(sqsPayload["ReceiveMessageResponse"]["ReceiveMessageResult"]["messages"][0]["Body"])
        ReceiptHandle = sqsPayload["ReceiveMessageResponse"]["ReceiveMessageResult"]["messages"][0]["ReceiptHandle"]
        response['s3BucketName'] = body["bucketName"]
        response['s3ObjectKey'] = body["objectKey"]
        response['s3ObjectUrl'] = body["objectUrl"]
        response['snsTopicArn'] = body["snsTopicArn"]
        response['receiptHandle'] = ReceiptHandle
        response['errorCode'] =  200
    except Exception as e:
        logger.error('Error: {}'.format(e))
        response['errorCode'] =  500
        response['errorMessage'] =  'Could not retrieve any records from the queue !!!'
    return response
