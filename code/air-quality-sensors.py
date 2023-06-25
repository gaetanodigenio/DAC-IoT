import config
import boto3
import random
import datetime
import json

sqs = boto3.resource('sqs', endpoint_url = config.endpoint_url)

#send messages on every queue dedicated to DAC sensors
for i in range(len(config.queue_names)):
    queue = sqs.get_queue_by_name(QueueName=config.queue_names[i])
    if random.random() < 0.21:
        #generate error on error queue
        queue_error = sqs.get_queue_by_name(QueueName="errors")
        error_msg = '{"device_type": "%s","error_date": "%s"}' % ("Air quality sensor", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print(error_msg)
        queue_error.send_message(MessageBody=error_msg)
        print("error sent")
    else:
        #generate data on the DAC_serialNumber queue
        for j in range(50):
            city = config.city[i]
            #generate timestamps adding 2 seconds each time
            time = (datetime.datetime.now() + datetime.timedelta(seconds = j * 300)).strftime("%Y-%m-%d %H:%M:%S")
            co2 = random.randint(0, 3000)
            location = config.location[i]
            data = {
                'time' : str(time),
                'city' : str(city),
                'location' : str(location),
                'co2' : int(co2)
            }
            queue.send_message(MessageBody=json.dumps(data))
        print("air data sent on air quality queue")
