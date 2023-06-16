import boto3
import config
import json

def lambda_handler(event, context):
    #connect to sqs and dynamodb
    sqs = boto3.resource('sqs', endpoint_url="http://host.docker.internal:4566")
    dynamodb = boto3.resource('dynamodb', endpoint_url="http://host.docker.internal:4566")

    #get data from the queue
    queue = sqs.get_queue_by_name(QueueName=config.queue_names[0])
    msgs = []
    previous_DAC_status = False

    response = queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=10, VisibilityTimeout=30)
    if response:
        msgs.extend(response)
        for message in msgs:
            content = (json.loads(message.body))
            print(content)
            print(type(content))

            #check CO2 levels
            if content['co2'] > 1000:
                current_DAC_status = True
            else:
                current_DAC_status = False

            if previous_DAC_status != current_DAC_status:
                if current_DAC_status == True:
                    print(f"DAC system activated! Critical air quality, CO2 levels at {content['co2']}")
                else:
                    print(f"DAC system is currently off -> CO2 levels at {content['co2']}")
                previous_DAC_status = current_DAC_status

            #create table on the db and insert data
            table = dynamodb.Table('DAC_1')
            item = {
                'time' : content['time'], 
                'DAC_Serial' : config.DAC_Serial[0],
                'city' : content['city'],
                'location' : content['location'],
                'co2' : content['co2'],
                'DAC_status' : current_DAC_status
            }
            table.put_item(Item = item)
            print(f"Stored item {item}")