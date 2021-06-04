#!/usr/bin/python
import json
import sys
import getopt

jsonObject = {
	"language": "GRAPHQL",
	"text": ""
}

def main(argv):
    inputfile = ''
    
    try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
      
    except getopt.GetoptError:
      # print ('stringify-json.py -i <inputfile>')
      sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            # print ('stringify-json.py -i <inputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
            with open(inputfile) as json_file:
              jsonObject["text"] = json_file.read()
              print(json.dumps(jsonObject))  
            # print ('Input file is "', inputfile)

if __name__ == "__main__":
   main(sys.argv[1:])
