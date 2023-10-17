import boto3
import json
import logging
import datetime
import glob
import os
from operator import attrgetter
from custom_encoder import CustomEncoder
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName = 'agent_scorecard_performance'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)

getMethod = 'GET'
postMethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'
healthPath = '/health'
issueCodePath= '/issuecode'
agentsPath= '/agents'
agentsAllPath= '/agentsall'
availableAgents = []

def lambda_handler(event, context):
    #
    region='us-east-1'
    try:
        startFile= '['
        endFile = ']'
        bucket = 'agent-performance'
        key = getLatestFile()
        #print(key)
        # get a handle on s3
        session = boto3.Session(region_name=region)
        s3 = session.resource('s3')
        obj = s3.Object(bucket,key)
        # read the contents of the file
        data = obj.get()['Body'].read().decode('utf-8')
        # Replace the target string
        data = data.replace('}{"AWSAccountId', '},{"AWSAccountId')
        final_data = startFile + data + endFile
        json_data = json.loads(final_data)
        
        for agent_list in json_data:
            availableSlots = agent_list['CurrentAgentSnapshot']['Configuration']['RoutingProfile']['Concurrency'][0]['AvailableSlots']
            maximumSlots = agent_list['CurrentAgentSnapshot']['Configuration']['RoutingProfile']['Concurrency'][0]['MaximumSlots']
            agentStatus = agent_list['CurrentAgentSnapshot']['AgentStatus']['Type']
            if agentStatus == "ROUTABLE" and availableSlots > 0 :
                #print(agentStatus)
                availableAgents.append(agent_list['CurrentAgentSnapshot']['Configuration']['Username'])
                #print(availableAgents)
    except:
        logger.exception('Error from awsconnect file!!')
        
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)
    elif httpMethod == getMethod and path == issueCodePath:
        response = getAgentsDetail(event['queryStringParameters']['issue_code'])
    elif httpMethod == getMethod and path == agentsAllPath:
        response = getAgentsAllDetail()
    elif httpMethod == postMethod and path == agentPath:
        response = saveAgentDetail(json.loads(event['body']))
    else:
        response = buildResponse(404, 'Not Found')

    return response

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
    #print(fileName)
    return fileName

def minTwoDigits(n):
  return ("0"+str(n)) if n < 10 else str(n)

def getAgentsAllDetail():
    try:
        response = table.scan()
        result = response['Items']

        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            result.extend(response['Items'])
        
        body = {
            'agents': response
        }
        return buildResponse(200, body)
    except:
        logger.exception('Error from getAgentsAllDetail !!')

def getAgentsDetail(issuetype):
    try:
        response = table.query(
            KeyConditionExpression=Key('issue_code').eq(issuetype),
            ScanIndexForward= False
        )
        
        uniqueAvailableAgents = list(set(availableAgents))
        final_body = []
        for agent_list in response['Items']:
            if(agent_list['ldap'] in uniqueAvailableAgents and len(final_body) != 1):
                final_body.append({'ldap' : agent_list[l]})
        if len(final_body) == 0 :
            final_body.append({'ldap' : 'Not Found'})
        body = final_body 

        return buildResponse(200, body)
    except:
        logger.exception('Error from getAgentsDetail !!')
        
def saveAgentDetail(requestBody):
    try:
        table.put_item(Item=requestBody)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return buildResponse(200,body)
    except:
        logger.exception('Error from saveAgentDetail !!')


def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Access-Control-Allow-Origin' : '*',
            'Content-Type': 'application/json'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response