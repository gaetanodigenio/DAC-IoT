import json
import config
import urllib3

def lambda_handler(event, context):
    key = config.IFTTkey
    url = "https://maker.ifttt.com/trigger/sensor_error/with/key/" + key
    print(type(event))
    print(event)
    payload = event['Records'][0]['body']
    payload1 = json.loads(str(payload))

    #device_type = payload1['device_type']
    date_error = payload1['error_date']
    
    http = urllib3.PoolManager()
    headers = {'Content-Type': 'application/json'}
    body = json.dumps({"Value1": date_error}).encode('utf-8')
    
    response = http.request('POST', url, body=body, headers=headers)