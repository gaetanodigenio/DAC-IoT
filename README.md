# DAC-IoT
Serverless computing for IoT course project

# How to install and use 
## Prerequisites
1. [Docker](https://www.docker.com/)
2. [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
3. [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html)

## Setting up the environment
1. **Clone the repository**
```
git clone https://github.com/gaetanodigenio/DAC-IoT.git
```
2. **Launch LocalStack**
```
docker run --rm -it -p 4566:4566 -p 4571:4571 -v /var/run/docker.sock:/var/run/docker.sock -e DEBUG=1 localstack/localstack
```
NOTE: "-e DEBUG" is used to see all the logs and eventual problems while executing on LocalStack, it can be removed in the command if not needed.
Also "-v /var/run/docker.sock:/var/run/docker.sock" is used in case in the execution of lambda function an error (ResourceConflictException) with a state: Failed is occurred.

3. **Create the SQS queues needed**
```
aws sqs create-queue --queue-name errors --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name AirQualityQueue --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name CO2PurityQueue --endpoint-url=http://localhost:4566
```
check if they have been succesfully created using
```
aws sqs list-queues --endpoint-url=http://localhost:4566 
```

4. **Create the DYNAMODBs and check the tables with a GUI**
```
python3 createDBs.py
aws dynamodb list-tables --endpoint-url=http://localhost:4566
DYNAMO_ENDPOINT=http://0.0.0.0:4566 dynamodb-admin
```
then use a browser to go to
```
http://localhost:8001
```
5. **Create an IFTT applet**
- Go to [IFTT](https://ifttt.com/explore) and sign-up or login.
- Click "create" to create a new applet
- Click "If this" and add a "webhooks" service
- Select "Receive a web request" and write "sensor_error" in the "Event Name" field.
- Save it and create the trigger
- In the applet page click Then That, type "email" in the search bar, and select Email.
- Click Send me an email and fill the "Subject" writing "A sensor encountered an error", then fill the body writing "The air quality sensor error generated an error, date {{Value1}}."
- Save all and finish.
- Modify the IFTTKey within the config.py with your IFTT applet key. The key can be find clicking on the icon of the webhook and clicking on Documentation.

6. **Create the lambda function for email errors**
```
aws iam create-role --role-name lambdarole --assume-role-policy-document file://role_policy.json --query 'Role.Arn' --endpoint-url=http://localhost:4566

aws iam put-role-policy --role-name lambdarole --policy-name lambdapolicy --policy-document file://policy.json --endpoint-url=http://localhost:4566


zip sendError.zip sendEmail.py config.py

aws lambda create-function --function-name sendEmail --timeout 250 --zip-file fileb://sendError.zip --handler sendEmail.lambda_handler --runtime python3.10 --role arn:aws:iam::000000000000:role/lambdarole --endpoint-url=http://localhost:4566
```
now create a source mapping event between the SQS errors and the lambda to automatically send an email when an error is written on the queue
```
aws lambda create-event-source-mapping --function-name sendEmail --batch-size 5 --maximum-batching-window-in-seconds 60 --event-source-arn arn:aws:sqs:us-east-2:000000000000:errors --endpoint-url=http://localhost:4566
```

7. **Launch the air quality monitoring sensor many times**
```
python3 air-quality-sensor.py
```
if an error is generated on the queue, an email should have been received.

8. **Create the lambda function for air quality monitoring**

```
aws iam create-role --role-name lambdarole --assume-role-policy-document file://role_policy.json --query 'Role.Arn' --endpoint-url=http://localhost:4566

aws iam put-role-policy --role-name lambdarole --policy-name lambdapolicy --policy-document file://policy.json --endpoint-url=http://localhost:4566

zip air-carbon-analysis.zip air-carbon-analysis.py config.py

aws lambda create-function --function-name air-carbon-analysis --timeout 250 --zip-file fileb://air-carbon-analysis.zip --handler air-carbon-analysis.lambda_handler --runtime python3.9 --role arn:aws:iam::000000000000:role/lambdarole --endpoint-url=http://localhost:4566
```
invoke it manually if wanted
```
aws lambda invoke --function-name air-carbon-analysis out --endpoint-url=http://localhost:4566
```
add a cloudwatch event to trigger the function every 5 minutes
```
????????????????
```

9. **Launch the carbon purity/quality sensor**
```
python3 carbon-quality-sensor.py
```

10. **Create the lambda function for price forecasting**
```
aws iam create-role --role-name lambdarole --assume-role-policy-document file://role_policy.json --query 'Role.Arn' --endpoint-url=http://localhost:4566

aws iam put-role-policy --role-name lambdarole --policy-name lambdapolicy --policy-document file://policy.json --endpoint-url=http://localhost:4566

zip priceForecasting.zip priceForecasting.py config.py

aws lambda create-function --function-name priceForecasting --timeout 250 --zip-file fileb://priceForecasting.zip --handler priceForecasting.lambda_handler --runtime python3.10 --role arn:aws:iam::000000000000:role/lambdarole --endpoint-url=http://localhost:4566
```
invoke it manually
```
aws lambda invoke --function-name priceForecasting out --endpoint-url=http://localhost:4566
```





