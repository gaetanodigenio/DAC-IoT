import boto3
import datetime
import config
import random
import json


sqs = boto3.resource('sqs', endpoint_url = config.endpoint_url)

#send messages on every queue dedicated to CO2 purity sensors
for i in range(len(config.queue_names2)):
    queue = sqs.get_queue_by_name(QueueName=config.queue_names2[i])

    if random.random() < 0.21:
        queue_error = sqs.get_queue_by_name(QueueName = "errors")
        error_msg = '{"device_type": "%s","error_date": "%s"}' % ("Carbon purity sensor", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print(error_msg)
        queue_error.send_message(MessageBody=error_msg)
        print("error sent")
    else:
        #generate data on the CO2_analysis(serialNumber) queue
        for j in range(30):
            city = config.city[i]
            #generate timestamps adding 2 seconds each time
            time = (datetime.datetime.now() + datetime.timedelta(seconds = j * 2)).strftime("%Y-%m-%d %H:%M:%S")
            purityIndex = random.randint(1, 3)
            tons = round(random.uniform(0.1, 2.0), 2)
            data = {
                "time" : str(time),
                "city" : str(city),
                "purityIndex" : int(purityIndex),
                "tons" : tons
            }
            queue.send_message(MessageBody=json.dumps(data))
        print("Carbon purity data sent on CO2 purity queue")