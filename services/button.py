import RPi.GPIO as GPIO
import time
import boto3
import json
import os
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


#GPIO ports configured in the rpi workshop is 27

def handler(event,context):
    GPIO_PORT = os.environ['GPIO_PORT'] # The GPIO Port is received as an environment variable
    response = {}
    try:
        response ['ButtonClicked']= int(buttonListener(GPIO_PORT))
    except Exception as e: 
        logger.error('Error: {}'.format(e))
        response['errorMessage'] = e
    return response


def buttonListener(GPIO_PORT):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_PORT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setwarnings(False)
    while True:
        input_state = GPIO.input(GPIO_PORT)
        if input_state == False:
            print('Button Pressed')
            time.sleep(0.2)
            return True

def main():
    while True:
        handler('','')

main()