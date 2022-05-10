#!/usr/bin/env python3
from datetime import datetime
import csv
import pandas as pd
import numpy as np
from bluepy import btle
from bluepy.btle import Scanner, Peripheral, Characteristic, ScanEntry, UUID
import time
import miband4_lib as mib
scanner = Scanner()
frames = []
hr = []
heart = []
result = pd.DataFrame(columns=['DEV_ADDR','DEV_RSSI','HR'])
while True:
    devs=scanner.scan(1);
    res=np.array([(datetime.now(),dev.getValueText(btle.ScanEntry.COMPLETE_LOCAL_NAME), dev.getValueText(btle.ScanEntry.SHORT_LOCAL_NAME), dev.addr, dev.addrType,dev.connectable, dev.rssi,[]) for dev in devs])
    df=pd.DataFrame(res,columns=['DATETIME','COMPL_LOC_NAME','SHORT_LOC_NAME','DEV_ADDR','DEV_ADDR_TYPE','DEV_CONNECTABLE','DEV_RSSI','HR'])
    mac_ad = df[df['COMPL_LOC_NAME']=='Mi Smart Band 4'][['DEV_ADDR','DEV_RSSI']] #prendo solo i dispositivi di interesse
    rssi_dev1 = df[df['DEV_ADDR']=='f8:58:1d:1d:d3:b7']['DEV_RSSI'] #mi trovo gli rssi di entrambi (ovviamente si può automatizzare con un for)
    rssi_dev2 = df[df['DEV_ADDR']=='f0:96:ca:e3:92:c2']['DEV_RSSI']
    rssi1 = np.array(rssi_dev1) #lo trasformo in array per poterlo utilizzare come dato
    rssi2 = np.array(rssi_dev2)
    #result = result.append(mac_ad)
    mac_array = np.unique(np.array(mac_ad['DEV_ADDR'])) #creo la lista dei mac address
    #RSSI_array = np.array(mac_ad['DEV_RSSI'])
    #mac_array = mac_array[1]
    #print('sono quiiiii',mac_array)
    for mac in mac_array:
            #print('qua ci entrooo',mac,'aa')
            if mac == 'f8:58:1d:1d:d3:b7':
                #print('f8')
                hr= mib.run(mac,"D50271FC8E0AA5E0BE7CFCD27F7AE336")
                hr = str(hr)
                #global heart
                heart = pd.DataFrame({'DEV_ADDR':mac,'DEV_RSSI':rssi1,'HR':[hr]})
                result = result.append(heart)
                print(result)
            if mac == "f0:96:ca:e3:92:c2":
                #print('f0')
                hr= mib.run(mac,"FDC91E5E86196E7AADAA924F2F3A66F5")
                hr = str(hr)
                #global heart
                heart = pd.DataFrame({'DEV_ADDR':mac,'DEV_RSSI':rssi2,'HR':[hr]})
                result = result.append(heart)
                print(result)
            if mac!='f8:58:1d:1d:d3:b7' and "f0:96:ca:e3:92:c2":
                continue
            hr = []