import RPi.GPIO as GPIO
import time
import boto3
import json
import os
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


#GPIO ports configured in the rpi workshop are
# Green1 => 4 ; Green2 => 19; Green3 =>26
# Red1 => 12 ; Red2 => 24; Red3 => 23

def handler(event,context):
    GPIO_PORT = event["gpioPort"] # The GPIO Port is received from the ThingsGraph Flow
    LIGHT_STATE =  event["lightState"]  # 0 =>lights off; 1 => lights on; 2 => lights toggle
    response = {}
    try:
        response ['LightState']= changeLights(LIGHT_STATE,GPIO_PORT)
    except Exception as e: 
        logger.error('Error: {}'.format(e))
        response['errorMessage'] = e
    return response


def changeLights(LIGHT_STATE,GPIO_PORT):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_PORT,GPIO.OUT)
    GPIO.setwarnings(False)
    if (LIGHT_STATE == 0):
        GPIO.output(GPIO_PORT,GPIO.LOW)
    elif(LIGHT_STATE == 1):
        GPIO.output(GPIO_PORT,GPIO.HIGH)
    elif(LIGHT_STATE == 2):
        for _ in range(5):
            GPIO.output(GPIO_PORT,GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(GPIO_PORT,GPIO.LOW)
            time.sleep(0.2)
        LIGHT_STATE = 0
    return LIGHT_STATE