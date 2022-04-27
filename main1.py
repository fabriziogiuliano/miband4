#!/usr/bin/env python3
from datetime import datetime
import csv
import pandas as pd
import numpy as np
from bluepy import btle
from bluepy.btle import Scanner, Peripheral, Characteristic, ScanEntry, UUID
scanner = Scanner()
frames = []
result = pd.DataFrame(columns=['DATETIME','COMPL_LOC_NAME','SHORT_LOC_NAME','DEV_ADDR','DEV_ADDR_TYPE','DEV_CONNECTABLE','DEV_RSSI'])
while True:
	devs=scanner.scan(1);
	res=np.array([(datetime.now(),dev.getValueText(btle.ScanEntry.COMPLETE_LOCAL_NAME), dev.getValueText(btle.ScanEntry.SHORT_LOCAL_NAME), dev.addr, dev.addrType,dev.connectable, dev.rssi)
				for dev in devs])
	df=pd.DataFrame(res,columns=['DATETIME','COMPL_LOC_NAME','SHORT_LOC_NAME','DEV_ADDR','DEV_ADDR_TYPE','DEV_CONNECTABLE','DEV_RSSI'])
	result = result.append(df)
	result.to_csv("pippo_{}.csv".format(datetime.now()))
	print(res)
	"""
	with open('res.csv','w',encoding='utf-8',newline='\n') as csvfile:
	fieldnames = ['COMPL_LOC_NAME','SHORT_LOC_NAME','DEV_ADDR','DEV_ADDR_TYPE','DEV_CONNECTABLE','DEV_RSSI']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()
	writer.writerow({'COMPL_LOC_NAME':res.T[0],'SHORT_LOC_NAME':res.T[1],'DEV_ADDR':res.T[2],'DEV_ADDR_TYPE':res.T[3],'DEV_CONNECTABLE':res.T[4],'DEV_RSSI':res.T[5]})
	df=pd.read_csv("res.csv")
	print(df)
	"""      