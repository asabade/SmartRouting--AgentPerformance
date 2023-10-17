import json
import boto3
import os
import datetime
import glob
import os
from operator import attrgetter

def lambda_handler(event, context):
    # TODO implement
    
    x = getLatestFile()
    print(x)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def getLatestFile():
    s3 = boto3.resource('s3')
    fileName = ""
    
    YEAR = datetime.date.today().year
    MONTH = datetime.date.today().month
    DAY = datetime.date.today().day
    HOUR = datetime.datetime.now().hour
    #MINUTE = datetime.datetime.now().minute
    #SECONDS  = datetime.datetime.now().second
    #print(YEAR, MONTH, DAY, HOUR, MINUTE, SECONDS)
    
    bucket = "agent-performance"
    #prefix = "connect/AEs/2022/02/14/08/"
    prefix="connect/AEs/"+str(YEAR)+"/"+minTwoDigits(MONTH)+"/"+minTwoDigits(DAY)+"/"+minTwoDigits(HOUR)+"/"
    print(prefix)
    allObj=s3.Bucket(bucket).objects.filter(Prefix=prefix).all()
    # sort the objects based on 'obj.last_modified'
    sortedObj = sorted(allObj, key=attrgetter('last_modified'))
    if(len(sortedObj) == 0):
        #print("No File Found")
        fileName = "No File Found"
    else:
        latestFile = sortedObj.pop()
        #print(latestFile.key)
        fileName = latestFile.key
    #for obj in allFile:
    #    print(obj.last_modified)
    #    print(obj.key)
    
    return fileName
    
def minTwoDigits(n):
  return ("0"+str(n)) if n < 10 else str(n)