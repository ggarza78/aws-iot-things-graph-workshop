#!/bin/bash
projectPath=$(pwd)
echo "Installing necessary libraries"
sudo yum install jq -y

# Prepare the model files by placing proper region name and account ID within them 
accountNumber=$(/usr/local/bin/aws sts get-caller-identity|jq -r '.Account')
region=$(/usr/local/bin/aws configure get region)


cd $projectPath
mkdir $projectPath/models-tmp
rsync -av --progress models/ models-tmp --exclude ml


find models-tmp -type f -exec sed -i -e "s/acctID/${accountNumber}/g" {} \;
find models-tmp -type f -exec sed -i -e "s/regionName/${region}/g" {} \;

# Replacing Lambda function Alias with Latest Lambda version number
#This is to get around the issue where ThingsGraph Flows deployed on GreenGrass do not understand ALIAS
#This workaround should be removed when fixed in ThingsGraph
grep -i Latest $projectPath/models-tmp/lambdas/* | awk -F ':' '{print $(NF-1)}'| while read -r line ; do
    functionAlias=$(/usr/local/bin/aws lambda get-alias --function-name "$line" --name Latest) 
    functionVersion=$(echo $functionAlias |jq '.FunctionVersion'| sed -e 's/^"//' -e 's/"$//')
    echo "Changing Lambda Reference from ${line}:Latest to ${line}:$functionVersion !!!"
    find $projectPath/models-tmp/lambdas -type f -exec sed -i -e "s/${line}:Latest/${line}:${functionVersion}/g" {} \;
done

#stringify models and upload them into Things Graph 
echo "Scanning to model file in $PWD/models !!!"
for f in "$projectPath/"models-tmp/*; do
    if [ -d "$f" ]; then
        if [[ "$f" != *"flows"* ]]; then
            for ff in $f/*
                do
                    echo "Creating Things Graph model for file $ff !!!"
                    python3.6 $projectPath/scripts/stringify-model.py -i "$ff" >model-tmp.json
                    /usr/local/bin/aws iotthingsgraph upload-entity-definitions --document file://model-tmp.json
                done
        fi
    fi
done