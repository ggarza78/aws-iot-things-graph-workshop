'''
PLACEHOLDER function
This function is responsible for identifying the type of the gauge
and responds with gauge configurations
ATM we only have a single gauge type that we will use as the default selection
'''

import boto3
import json
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event,context):
    response = {'s3BucketName':'','s3ObjectKey':'','min_angle':0,'max_angle':0,'min_value':0,'max_value':0,'units':'','threshold':0,'errorCode':500,'errorMessage':'','gaugeType':'','gaugeID':''}
    try:
        bucket_name =  event["s3BucketName"]
        image_key =  event["s3ObjectKey"]
        response = GetTemperatureGauge(bucket_name,image_key)
    except Exception as e: 
        logger.error('Error: {}'.format(e))
        response['errorMessage'] = e
    return response


def GetTemperatureGauge(bucket_name,image_key):
    response = {}
    response['s3BucketName'] = bucket_name
    response['s3ObjectKey'] = image_key
    response['min_angle'] = 90
    response['max_angle'] = 270
    response['min_value'] = 0
    response['max_value'] = 100
    response['units'] = 'C'
    response['threshold'] = 80
    response['errorCode'] = 200
    response['gaugeType'] = 'temperature-gauge'
    response['gaugeID'] = 'ID123'
    return response

def GetTSpeedGauge(bucket_name,image_key):
    response = {}
    response['s3BucketName'] = bucket_name
    response['s3ObjectKey'] = image_key
    response['min_angle'] = 90
    response['max_angle'] = 270
    response['min_value'] = 0
    response['max_value'] = 220
    response['units'] = 'Kmh'
    response['threshold'] = 100
    response['errorCode'] = 200
    response['gaugeType'] = 'speed-gauge'
    response['gaugeID'] = 'ID1234'
    return response