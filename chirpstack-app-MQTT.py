from __future__ import print_function
from datetime import datetime
import paho.mqtt.client as mqtt
import psutil
import json
import time
import base64
import string
import pandas as pd

config = {"host" : "10.8.9.27", "token":"TFyCMKn7IOl0JhYUk1J0"}
#Open MongoDB
import pymongo
myclient = pymongo.MongoClient("mongodb://{}:27017/".format(config["host"]))
mydb = myclient["SAWE-BLE"]
#mycol = mydb["pycom_solar"] #collection first experiment
#mycol = mydb["pycom_solar_2"] #collection second experiment (battery voltage + solar panel voltage from ADC)
mycol = mydb["BLE_HR_LORA"] #collection new ADC acquistion + machine Temperature + v_solar stats

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    #client.subscribe("application/+/device/+/event/up/#")  # Subscribe to the topic
    client.subscribe("application/+/device/+/event/#")  # Subscribe to the topic
    #client.subscribe("application/+/device/+/event/frame/#")  # Subscribe to the topic


def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    print("Message received-> " + msg.topic + " " + str(msg.payload))  # Print a received msg
    mm=json.loads(msg.payload)
    print('mm',mm)
    #print('mm è: ',mm['data'])
    try:
        #message = base64.b64decode(mm["data"]).decode('utf8')
        message = base64.b64decode(mm["data"])#.decode(encoding='utf-8')
        message=list(message)
        #message = ''.join([x if x in string.printable else '' for x in message]).replace("\r","") #remove not printable chars
        print(message)
        t = 0
        l = int(len(message))
        result = []
        for i in range(0, l, 8):
            result.append(message[i:8 * (t + 1)])
            t = t + 1
        f = len(result)
        addr = []
        list_to_panda = []
        for i in range(f):
            addr = []
            values = ':'.join(str(hex(v)[2:]) for v in result[i][:6])
            addr.append(values)
            result[i][6] = result[i][6] * (-1)
            addr.extend(result[i][6:])
            list_to_panda.append(addr)
        hr_db = pd.DataFrame(list_to_panda, columns=['DEV_ADDR', 'DEV_RSSI', 'HR'])
        hr_db.insert(0, "DATETIME", [datetime.now()] * f, True)
        #print(mm)
        #message=json.loads(message)
    
        data={"datetime": datetime.now(), "rxInfo":mm["rxInfo"],"txInfo":mm["txInfo"],"fCnt":mm["fCnt"],"data":message}

        # Open MongoDB
        myclient = pymongo.MongoClient("mongodb://{}:27017/".format(config["host"]))
        mydb = myclient["BLE_scanner"]
        # mycol = mydb["pycom_solar"] #collection first experiment
        # mycol = mydb["pycom_solar_2"] #collection second experiment (battery voltage + solar panel voltage from ADC)
        mycol = mydb["LoRa_detec"]  # collection new ADC acquistion + machine Temperature + v_solar stats

        # x = mycol.insert_many(hr_db)
        hr_db = hr_db.to_dict(orient='list')

        result = mycol.insert_one(hr_db).inserted_id
        #print(json.dumps(data,sort_keys=True, indent=4))
        #print(json.dumps(data))

    except Exception as e:
        print(e)

def on_subscribe(client, userdata, mid, granted_qos):  # subscribe to mqtt broker
    print("Subscribed", userdata)


client = mqtt.Client("client")  # Create instance of client with client ID “digi_mqtt_test”
client.on_connect = on_connect  # Define callback function for successful connection
client.on_subscribe = on_subscribe
#client.username_pw_set(config["token"])
client.connect(config["host"], 1883, 60)
client.on_message = on_message  # Define callback function for receipt of a message

# client.connect("m2m.eclipse.org", 1883, 60)  # Connect to (broker, port, keepalive-time)
client.loop_forever()  # Start networking daemon


