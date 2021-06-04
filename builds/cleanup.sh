 
 #!/bin/bash
 # This script is used to remove some unnessary packages from cloud9 to open up disk space for the workshop
 # CAUTION : Do not use this script in your active dev environment sice it can be harmfull to your environment.
 echo "$C9_HOSTNAME"
 if [ -n "$C9_HOSTNAME" ]
    then
        echo "Freeing Up space by removing unecessay libraries for Ruby, Nodejs, etc.. on cloud9 !!!"
        rvm uninstall --gems $(rvm list strings | tr "\n" ',')
        rvm cleanup all
        rm -rf /home/ec2-user/.nvm
        sudo  rm -rf /tmp/* 
        sudo rm -rf /usr/lib/golang
    else
        echo "This is not a Cloud9 environment skipping cleanup !!!"
    fi