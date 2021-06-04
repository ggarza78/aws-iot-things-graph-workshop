#!/bin/bash

# Specify the desired volume size in GiB as a command-line argument. If not specified, default to 20 GiB.
SIZE=${1:-20}

# Display the current size of the file system
echo "current / partition details:  $(df -h | grep /$ ) !!!"

# Install the jq command-line JSON processor.
sudo yum -y install jq

# Get the ID of the envrionment host Amazon EC2 instance.
INSTANCEID=$(curl http://169.254.169.254/latest/meta-data//instance-id)

# Get the ID of the Amazon EBS volume associated with the instance.
VOLUMEID=$(aws ec2 describe-instances --instance-id $INSTANCEID | jq -r .Reservations[0].Instances[0].BlockDeviceMappings[0].Ebs.VolumeId)

# Resize the EBS volume.
aws ec2 modify-volume --volume-id $VOLUMEID --size $SIZE

# Wait for the resize to finish.
while [ "$(aws ec2 describe-volumes-modifications --volume-id $VOLUMEID --filters Name=modification-state,Values="optimizing","completed" | jq '.VolumesModifications | length')" != "1" ]; do
  sleep 1
done

# Get the / filesystem
filesystem=$(df -h | grep /$|awk -F ' ' '{ print $1 }')

echo "$filesystem"

# Rewrite the partition table so that the partition takes up all the space that it can.
sudo growpart $filesystem 1

# Expand the size of the file system.
sudo resize2fs "$filesystem"

echo "Updated / partition details:  $(df -h | grep /$ ) !!!"