import boto3
import config
import json
import datetime
from decimal import *


def lambda_handler(event, context):
    #connect to sqs and dynamodb
    sqs = boto3.resource('sqs', endpoint_url="http://host.docker.internal:4566")
    dynamodb = boto3.resource('dynamodb', endpoint_url="http://host.docker.internal:4566")

    #create table
    table = dynamodb.Table('CO2_Analysis2')

    #var database
    tonsUnderground = 0
    tonsLevel2 = 0
    earningsLevel2 = 0
    tonsLevel3 = 0 
    earningsLevel3 = 0

    #get data from the queue
    queue = sqs.get_queue_by_name(QueueName=config.queue_names2[1])
    msgs = []
    response = queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=10, VisibilityTimeout=30)
    if response:
        msgs.extend(response)
        for message in msgs:
            content = (json.loads(message.body))
            print(content)
            #calculate price, tons and forecasting
            if(content['purityIndex'] == 1):
                tonsUnderground += round(Decimal(content['tons']), 2)
            elif(content['purityIndex'] == 2):
                earningsLevel2 += round((Decimal(content['tons']) * 60), 2)
                tonsLevel2 += round(Decimal(content['tons']), 2)
            elif(content['purityIndex'] == 3): 
                earningsLevel3 += round((Decimal(content['tons'] * 80)), 2)
                tonsLevel3 += round(Decimal(content['tons']), 2)

    '''
    da memorizzare nel db
    4) stima quantità futura
    '''

    time = datetime.datetime.now()
    #insert data on db
    item1 = {
        'time' : (time + datetime.timedelta(seconds = 1)).strftime("%Y-%m-%d %H:%M:%S"),
        'machineSerial' : config.purity_machine_Serial[1],
        'purityIndex' : 1,               
        'city' : content['city'],
        'tonsUnderground' : str(tonsUnderground)
    }
    table.put_item(Item = item1)

    #insert data on db
    item2 = {
        'time' : (time + datetime.timedelta(seconds = 3)).strftime("%Y-%m-%d %H:%M:%S"),
        'machineSerial' : config.purity_machine_Serial[1],
        'purityIndex' : 2,               
        'city' : content['city'],
        'totalTons' : str(tonsLevel2),
        'totalEarnings' : str(earningsLevel2)
    }
    table.put_item(Item = item2)


    #insert data on db
    item3 = {
        'time' : (time + datetime.timedelta(seconds = 5)).strftime("%Y-%m-%d %H:%M:%S"),
        'machineSerial' : config.purity_machine_Serial[1],
        'purityIndex' : 3,                
        'city' : content['city'],
        'totalTons' : str(tonsLevel3),
        'totalEarnings' : str(earningsLevel3)
    }
    table.put_item(Item = item3)
  
    
    print(f"Stored item {item1}, {item2}, {item3}")