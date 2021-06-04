import time
import boto3
import json
import os
import logging
from picamera import PiCamera

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event,context):
    BUCKET_NAME = event["BucketName"]
    IMAGE_PATH = os.environ['IMAGE_PATH']
    response = {'s3BucketName':'','s3ObjectKey':'','errorCode':500,'errorMessage':''}
    try:
        objectKey = captureImage(IMAGE_PATH,BUCKET_NAME)
        s3Upload(IMAGE_PATH,BUCKET_NAME,objectKey)
        response['s3BucketName'] = BUCKET_NAME
        response['s3ObjectKey'] = objectKey
        response['errorCode'] = 200
    except Exception as e: 
        logger.error('Error: {}'.format(e))
        response['errorMessage'] = e
    return response

def captureImage(imagePath,BucketName):
    imagePath = imagePath
    objectKey= str(int(time.time()))+ '.jpg'
    imageFile =imagePath+ '/'+objectKey
    camera = PiCamera()
    camera.start_preview()
    camera.resolution = (1024, 768)
    camera.capture(imageFile)
    camera.stop_preview()
    camera.close()
    return objectKey

def s3Upload(imagePath,bucketName,objectKey):
    s3 = boto3.client("s3", region_name= os.environ['AWS_REGION'])
    file_obj = s3.upload_file(imagePath+'/'+objectKey,bucketName, objectKey)