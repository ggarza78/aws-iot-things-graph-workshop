#!/bin/bash

if [ -z "$1" ]
  then
    echo "No S3 Bucket Name supplied !!!"
    exit 1
fi
PROJECT_ROOT=$(pwd)
# This script is responsible for setting up all the dependencies requiered by cloud9
echo "Installing necessary libraries"
sudo yum install zip jq gcc openssl-devel bzip2-devel libffi-devel -y

#Updating AWS CLI to V2 if needed
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update  

#install python3.7
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz
sudo tar xzf Python-3.7.4.tgz
cd Python-3.7.4
sudo ./configure --enable-optimizations
sudo make altinstall
sudo rm /usr/src/Python-3.7.4.tgz
sudo cp /usr/local/bin/python3.7 /usr/bin/

cd  $PROJECT_ROOT
#python3.7 -m pip install --target $PWD/libs/  --system opencv-python numpy boto3 opencv-contrib-python cfnresponse requests matplotlib
sudo python3.7 -m pip install --upgrade pip setuptools wheel
#python3.7 -m pip install --target $PWD/libs/  opencv-python numpy cfnresponse opencv-contrib-python requests matplotlib

python3.7 -m pip install --target $PROJECT_ROOT/libs/  opencv-python-headless numpy cfnresponse requests matplotlib
cd  $PROJECT_ROOT/libs

# Remove botcore library from libs
rm -rf botocore*

echo "creating a zip artifact containing all the lambda functions"
zip -r9 ../packages/things-graph-workshop.zip .

cd  $PROJECT_ROOT/services

# create a zip file artifacts that is used to create the Lambda functions
zip -g ../packages/things-graph-workshop.zip * 

cd $PROJECT_ROOT


#Upload artifiacts to S3 Bucket
echo "uploading created artifacts to s3://$1/ !!!"
/usr/local/bin/aws s3 cp packages/things-graph-workshop.zip  "s3://$1/"
/usr/local/bin/aws s3 cp models/ml/ "s3://$1/models/ml" --recursive