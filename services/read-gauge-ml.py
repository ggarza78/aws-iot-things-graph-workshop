import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np 
from PIL import Image
import boto3
import botocore.config
import os
from io import BytesIO
import time
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class RegModel(nn.Module):
    def __init__(self):
        super().__init__()
        layers = list(torch.hub.load('pytorch/vision:v0.5.0', 'resnet18', pretrained=True).children())[:-2]
        layers += [nn.Flatten()]
        layers += [nn.Linear(25088,1)]
        self.model_regr = nn.Sequential(*layers)
    def forward(self, x):
        return self.model_regr(x).squeeze(-1)
model_regr = RegModel()

def handler(event,context):
    timeStamp = int(time.time())
    try:
        image_key =  event["s3ObjectKey"]
        bucket_name =  event["s3BucketName"]
        image = get_image(bucket_name,image_key)
        proccessed_image = process_image(image)
        prediction = predict(proccessed_image)
        return{
            'gaugeReading' : prediction,
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



def get_image(bucket_name,image_key):
    # download the image, convert it to a NumPy array, and then read
    # it into OpenCV format
    s3 = boto3.client("s3", region_name=os.environ['AWS_REGION'])
    file_obj = s3.get_object(Bucket=bucket_name, Key=image_key)
    
    # reading the file content in bytes
    file_content = file_obj["Body"].read()
    
    return Image.open(BytesIO(file_content))

def process_image(img):
    
    # Get the dimensions of the image
    width, height = img.size
    
    
    #test RGB conversion
    img = img.convert('RGB')
    
    # Resize by keeping the aspect ratio, but changing the dimension
    # so the shortest size is 255px
    img = img.resize((255, int(255*(height/width))) if width < height else (int(255*(width/height)), 255))
    
    # Get the dimensions of the new image size
    width, height = img.size
    
    # Set the coordinates to do a center crop of 224 x 224
    left = (width - 224)/2
    top = (height - 224)/2
    right = (width + 224)/2
    bottom = (height + 224)/2
    img = img.crop((left, top, right, bottom))
    
    # Turn image into numpy array
    img = np.array(img)
    
    # Make the color channel dimension first instead of last
    img = img.transpose((2, 0, 1))
    
    # Make all values between 0 and 1
    img = img/255
    
    # Normalize based on the preset mean and standard deviation
    img[0] = (img[0] - 0.485)/0.229
    img[1] = (img[1] - 0.456)/0.224
    img[2] = (img[2] - 0.406)/0.225
    
    # Add a fourth dimension to the beginning to indicate batch size
    img = img[np.newaxis,:]
    
    # Turn into a torch tensor
    image = torch.from_numpy(img)
    image = image.float()
    print("image processed")
    return image
    
def load_model():
  print('Loading model from S3 !!!')
#   s3 = boto3.client("s3", region_name=os.environ['AWS_REGION'])
  s3 = boto3.client('s3', region_name=os.environ['AWS_REGION'], config=botocore.config.Config(s3={'addressing_style':'path'}))
  s3.download_file(os.environ['MODEL_BUCKET'], os.environ['MODEL_NAME'],os.environ['MODEL_FILE_NAME'])


def predict(image):
    print("start predict")
    torch.cuda._initialized=True
    device = torch.device('cpu')
    resourcePath = os.environ['MODEL_FILE_NAME']
    try:
        with open(resourcePath, 'rb') as f:
            print('model found in local drive !!!')
            model_regr.load_state_dict(torch.load(f, map_location=device))
            model_regr.eval()
            # Pass the image through our model
            output = model_regr(image)
            print(output)
            print(output[0].detach().numpy())
            # Reverse the log function in our output
            return output[0].detach().numpy().tolist()
    except IOError:
        print('model not found !!!')
        load_model()
        with open(resourcePath, 'rb') as f:
            model_regr.load_state_dict(torch.load(f, map_location=device))
            model_regr.eval()
            # Pass the image through our model
            output = model_regr(image)
            print(output)
            print(output[0].detach().numpy())
            # Reverse the log function in our output
            return output[0].detach().numpy()
        