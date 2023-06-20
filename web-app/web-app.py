from flask import Flask, render_template
import boto3
from operator import itemgetter
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import datetime 

app = Flask(__name__)
dynamodb = boto3.resource('dynamodb',  endpoint_url="http://localhost:4566")


def get_CO2_levels_db():
    table1 = dynamodb.Table('DAC_1')
    table2 = dynamodb.Table('DAC_2') 
    table3 = dynamodb.Table('CO2_Analysis1') 
    table4 = dynamodb.Table('CO2_Analysis2') 
    response1 = table1.scan()
    response2 = table2.scan()
    response3 = table3.scan()
    response4 = table4.scan()

    #sorting by time
    items1 = sorted(response1['Items'], key=itemgetter('time'))
    items2 = sorted(response2['Items'], key=itemgetter('time'))
    items3 = sorted(response3['Items'], key=itemgetter('time'))
    items4 = sorted(response4['Items'], key=itemgetter('time'))


    items = [
        {'items1' : items1},
        {'items2' : items2},
        {'items3' : items3},
        {'items4' : items4}
    ]
    return items

    
def CO2_forecasting():
    table1 = dynamodb.Table('DAC_1')
    table2 = dynamodb.Table('DAC_2') 
    response1 = table1.scan()
    response2 = table2.scan()
    sorted1 = sorted(response1['Items'], key=itemgetter('time'))
    sorted2 = sorted(response2['Items'], key=itemgetter('time'))
    data1 = [item['co2'] for item in sorted1]
    time1 = [item['time'] for item in sorted1]
    timePrevision1 = datetime.datetime.strptime(time1[len(time1) - 1], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(seconds=2)

    data2 = [item['co2'] for item in sorted2]
    time2 = [item['time'] for item in sorted2]
    timePrevision2 = datetime.datetime.strptime(time2[len(time2) - 1], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(seconds=2)


    # Prepare data for model training
    X1 = np.arange(len(data1)).reshape(-1, 1)
    y1 = data1

    X2 = np.arange(len(data2)).reshape(-1, 1)
    y2 = data2


    # Create and train the Random Forest model
    model1 = RandomForestRegressor(n_estimators=100, random_state=42)
    model2 = RandomForestRegressor(n_estimators=100, random_state=42)
    model1.fit(X1, y1)
    model2.fit(X2, y2)

    # make previsions
    X_future1 = np.arange(len(data1), len(data1) + 1).reshape(-1, 1)
    predictions1 = model1.predict(X_future1)

    X_future2 = np.arange(len(data2), len(data2) + 1).reshape(-1, 1)
    predictions2 = model2.predict(X_future2)

    ret = [data1, time1, predictions1, data2, time2, predictions2, str(timePrevision1), str(timePrevision2)]
    return ret
    

@app.route('/', methods = ['GET'])
def hello_world():
    items = get_CO2_levels_db()
    predictions = CO2_forecasting()
    return render_template("index.html", items = items, predictions=predictions)


if __name__ == "__main__":
    app.run(port = 8000, debug=True)
