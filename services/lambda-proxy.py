import time
import json
import boto3
import logging
import os


logger = logging.getLogger()
logger.setLevel(logging.INFO)

from io import BytesIO

def handler(event, context):
    timeStamp = int(time.time())
    try:
        print("event:",event)
        
        input_params = {
           's3ObjectKey' : event["s3ObjectKey"],
           's3BucketName' : event["s3BucketName"]
           }
        client = boto3.client('lambda')
        lambda_function_arn = context.invoked_function_arn
        account_id = lambda_function_arn.split(":")[4]
        function_name =  'arn:aws:lambda:'+os.environ['AWS_REGION']+':'+account_id+':function:'+event["lambdaFunctionName"]
       
        
        response = client.invoke(FunctionName = function_name, InvocationType = 'RequestResponse', Payload = json.dumps(input_params))
        response_payload = json.loads(response['Payload'].read().decode("utf-8"))

        return{
            'gaugeReading' : response_payload['gaugeReading'],
            'timeStamp' : timeStamp,
            'errorCode': 200,
            'errorMessage': ''
        }
    except Exception as e: 
        logger.error('Error: {}'.format(e))
        return {
        'gaugeReading' : 0,
        'timeStamp' : timeStamp,
        'errorCode': 500,
        'errorMessage': e
    }