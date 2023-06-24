# DAC-IoT using serverless computing

## Index
- [Project description](#Project-description)  
- [Implementation details](https://github.com/gaetanodigenio/DAC-IoT/blob/main/README.md#Implementation-details) 
- [Architecture](https://github.com/gaetanodigenio/DAC-IoT/blob/main/README.md#Architecture) 
- [How to install and use](https://github.com/gaetanodigenio/DAC-IoT/blob/main/README.md#How-to-install-and-use)

## Project description
The latest [IPCC](https://www.ipcc.ch/2022/04/04/ipcc-ar6-wgiii-pressrelease/) (International Panel on Climate Change) report clearly states that urgent climate action is needed to halve emissions by 2030. To do so, we must both drastically reduce emissions and remove legacy CO₂ emissions from the air. In order to permanently remove the CO₂ emissions we've captured, a DAC technology with CO₂ storage is combined and safely transport the isolated CO2 deep underground or reuse it in other industrial processes such as synthetic fuel production, construction materials, chemical production, sustainable agriculture and personal care products.<br>
DAC is a system that actively extracts CO2 directly from the air, regardless of its source, and subsequently sequesters or utilizes it to prevent its release back into the atmosphere. This technology employs a combination of advanced filters, chemical processes, and renewable energy sources to capture and separate CO2 molecules from the air.<br>

<img src="https://github.com/gaetanodigenio/DAC-IoT/blob/main/images/DAC.png" width="830" >
Now, since a DAC system is little bit expensive in terms of energy consumption to work, I believe it is a good idea to place this system near places where the CO2 release is higher instead of random places: near manufacturing industries (steel production, chemicals, cement, glass, and petroleum refineries for example), near a farm or fields or even near a city centre to filter transportation CO2 releases, and activate it when a certain CO2 release threshold is exceeded through smart sensors.<br>
This project shows an IIOT (Industrial IoT) application using IoT sensors and a serverless environment to reduce costs and development efforts using an event driven approach. 


## Implementation details
The implementation starts placing a sensor that captures air quality levels (specifically CO2 levels) and send those information to a queue (SQS). 
Then a lambda function is used and triggered every 5 minutes to process data in batch, controlling that when a specific CO2 release threshold is excedeed then the DAC system is activated.   
All the data is permanently stored in a DYNAMODB table. <br>
Also a forecasting of the next CO2 release is calculated using a random forest regressor algorithm.<br>
After the DAC system succesfully have filtered the air and isolated the CO2, the latter is sent to a CO2 purity analysis machine.
It's important to establish the purity, since based on that the packaged CO2 may be intended for a specific purpose (reused in other processes or be isolated deep underground). <br>
Reusing it in other industrial processes actually means that it can be sold to another company that need it at a specific price, based on the quantity and the purity of it. <br>
A second IoT sensor is then placed here to retrieve data about the purity and to send it on a SQS queue where a lambda function takes care of calculating the price based on quantity (tons) and purity (levels 1, 2, 3 the highest the purest) of the CO2.<br>
All the data here is also stored to a DYNAMODB table. <br>
If those sensor encouters an error during the data gathering, an email is automatically sent to the client using an IFTT applet, triggered by a lambda directly linked to the SQS using a source mapping event.  
In the end, a flask application allows the user to have a view over all those data and plots.  

## Architecture
<img src="https://github.com/gaetanodigenio/DAC-IoT/blob/main/images/Architettura.png" width="900" >

- IoT sensors are simulated using a python function and generating random data, one measures air quality (carbon levels) and the other carbon purity
- AWS SQS are used in order for lambda functions to retrieve and use data from the sensors, one SQS for each DAC machine
- AWS Lambda functions are used to analyze data and performing all the computation, one lambda for each SQS to improve scalability
- AWS Cloudwatch is used to trigger functions every 5 minutes
- Flask is used to create the web app using python as a backend programming language
- IFTT applet is used to send real email to the user
- DynamoDB is used to store data permanently using non relational db 
- AI ALGORITHM USED random forest regressor



## How to install and use 
### Prerequisites
1. [Docker](https://www.docker.com/)
2. [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
3. [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html)

### Setting up the environment
1. **Clone the repository wherever you like**
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
aws sqs create-queue --queue-name DAC_1 --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name DAC_2 --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name CO2_analysis1 --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name CO2_analysis2 --endpoint-url=http://localhost:4566
```
check if they have been succesfully created using
```
aws sqs list-queues --endpoint-url=http://localhost:4566 
```

4. **Create the DYNAMODBs and check the tables with a GUI**
```
cd code/
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
python3 air-quality-sensors.py
```
if an error is generated on the queue, an email should have been received.

8. **Create the lambda function for air quality monitoring**

```
aws iam create-role --role-name lambdarole --assume-role-policy-document file://role_policy.json --query 'Role.Arn' --endpoint-url=http://localhost:4566

aws iam put-role-policy --role-name lambdarole --policy-name lambdapolicy --policy-document file://policy.json --endpoint-url=http://localhost:4566

zip air-carbon-analysis1.zip air-carbon-analysis1.py config.py

aws lambda create-function --function-name air-carbon-analysis1 --timeout 250 --zip-file fileb://air-carbon-analysis1.zip --handler air-carbon-analysis1.lambda_handler --runtime python3.9 --role arn:aws:iam::000000000000:role/lambdarole --endpoint-url=http://localhost:4566
```
invoke it manually the first time
```
aws lambda invoke --function-name air-carbon-analysis1 out --endpoint-url=http://localhost:4566
```
add a cloudwatch event to trigger the function every 5 minutes
```
aws events put-rule --name air-carbon-analysis1 --schedule-expression 'rate(5 minutes)' --endpoint-url=http://localhost:4566

aws events list-rules --endpoint-url=http://localhost:4566

aws lambda add-permission --function-name air-carbon-analysis1 --statement-id air-carbon-analysis1 --action 'lambda:InvokeFunction' --principal events.amazonaws.com --source-arn arn:aws:events:us-east-2:000000000000:rule/air-carbon-analysis1 --endpoint-url=http://localhost:4566

aws events put-targets --rule air-carbon-analysis1 --targets file://target.json --endpoint-url=http://localhost:4566 
```

do the same for the air-carbon-analysis2 lambda function:
```
zip air-carbon-analysis2.zip air-carbon-analysis2.py config.py

aws lambda create-function --function-name air-carbon-analysis2 --timeout 250 --zip-file fileb://air-carbon-analysis2.zip --handler air-carbon-analysis2.lambda_handler --runtime python3.9 --role arn:aws:iam::000000000000:role/lambdarole --endpoint-url=http://localhost:4566
```
invoke it manually the first time
```
aws lambda invoke --function-name air-carbon-analysis2 out --endpoint-url=http://localhost:4566
```
add a cloudwatch event to trigger the function every 5 minutes
```
aws events put-rule --name air-carbon-analysis2 --schedule-expression 'rate(5 minutes)' --endpoint-url=http://localhost:4566

aws events list-rules --endpoint-url=http://localhost:4566

aws lambda add-permission --function-name air-carbon-analysis2 --statement-id air-carbon-analysis2 --action 'lambda:InvokeFunction' --principal events.amazonaws.com --source-arn arn:aws:events:us-east-2:000000000000:rule/air-carbon-analysis2 --endpoint-url=http://localhost:4566

aws events put-targets --rule air-carbon-analysis2 --targets file://target.json --endpoint-url=http://localhost:4566 

```


9. **Launch the CO2 purity/quality sensor**
```
python3 CO2-purity-sensors.py
```

10. **Create the lambda function for CO2-analysis1 ans CO2-analysis2**
```
aws iam create-role --role-name lambdarole --assume-role-policy-document file://role_policy.json --query 'Role.Arn' --endpoint-url=http://localhost:4566

aws iam put-role-policy --role-name lambdarole --policy-name lambdapolicy --policy-document file://policy.json --endpoint-url=http://localhost:4566

zip CO2-analysis1.zip CO2-analysis1.py config.py

aws lambda create-function --function-name CO2-analysis1 --timeout 250 --zip-file fileb://CO2-analysis1.zip --handler CO2-analysis1.lambda_handler --runtime python3.10 --role arn:aws:iam::000000000000:role/lambdarole --endpoint-url=http://localhost:4566
```
invoke it manually the first time
```
aws lambda invoke --function-name CO2-analysis1 out --endpoint-url=http://localhost:4566
```
add a cloudwatch trigger that call the lambda every 5 minutes
```
aws events put-rule --name CO2-analysis1 --schedule-expression 'rate(5 minutes)' --endpoint-url=http://localhost:4566

aws events list-rules --endpoint-url=http://localhost:4566


aws lambda add-permission --function-name CO2-analysis1 --statement-id CO2-analysis1 --action 'lambda:InvokeFunction' --principal events.amazonaws.com --source-arn arn:aws:events:us-east-2:000000000000:rule/CO2-analysis1 --endpoint-url=http://localhost:4566

aws events put-targets --rule CO2-analysis1 --targets file://target.json --endpoint-url=http://localhost:4566 
```

the same procedure is for CO2-analysis2:
```
zip CO2-analysis2.zip CO2-analysis2.py config.py

aws lambda create-function --function-name CO2-analysis2 --timeout 250 --zip-file fileb://CO2-analysis2.zip --handler CO2-analysis2.lambda_handler --runtime python3.10 --role arn:aws:iam::000000000000:role/lambdarole --endpoint-url=http://localhost:4566
```
invoke it manually the first time
```
aws lambda invoke --function-name CO2-analysis2 out --endpoint-url=http://localhost:4566
```
apply a cloudwatch that triggers the lambda every 5 minutes:
```
aws events put-rule --name CO2-analysis2 --schedule-expression 'rate(5 minutes)' --endpoint-url=http://localhost:4566

aws events list-rules --endpoint-url=http://localhost:4566


aws lambda add-permission --function-name CO2-analysis2 --statement-id priceForecasting --action 'lambda:InvokeFunction' --principal events.amazonaws.com --source-arn arn:aws:events:us-east-2:000000000000:rule/CO2-analysis2 --endpoint-url=http://localhost:4566

aws events put-targets --rule CO2-analysis2 --targets file://target.json --endpoint-url=http://localhost:4566 

```

in the end, just launch the flask application using:
```
cd web-app/
python3 web-app.py
```
then open it in a browser at the url http://127.0.0.1:8000/


