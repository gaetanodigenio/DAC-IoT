import boto3
import config

db = boto3.resource('dynamodb', endpoint_url=config.endpoint_url)

#air quality analysis table
table_DAC_1 = db.create_table(
    TableName = 'DAC_1',
    AttributeDefinitions = [
        {
            'AttributeName' : 'time',  
            'AttributeType' : 'S'
        }
    ],
    KeySchema = [
        {
            'AttributeName' : 'time',
            'KeyType' : 'HASH'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

table_DAC_2 = db.create_table(
    TableName = 'DAC_2',
    AttributeDefinitions = [
        {
            'AttributeName' : 'time',  
            'AttributeType' : 'S'
        }
    ],
    KeySchema = [
        {
            'AttributeName' : 'time',
            'KeyType' : 'HASH'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)



#CO2 purity analysis table
table_CO2_analysis1 = db.create_table(
    TableName = 'CO2_Analysis1',
    AttributeDefinitions = [
        {
            'AttributeName' : 'time',  
            'AttributeType' : 'S'
        }
    ],
    KeySchema = [
        {
            'AttributeName' : 'time',
            'KeyType' : 'HASH'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

table_CO2_analysis2 = db.create_table(
    TableName = 'CO2_Analysis2',
    AttributeDefinitions = [
        {
            'AttributeName' : 'time',  
            'AttributeType' : 'S'
        }
    ],
    KeySchema = [
        {
            'AttributeName' : 'time',
            'KeyType' : 'HASH'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

print('Table', table_DAC_1, 'created!')
print('Table', table_DAC_2, 'created!')
print('Table', table_CO2_analysis1, 'created!')
print('Table', table_CO2_analysis2, 'created!')
