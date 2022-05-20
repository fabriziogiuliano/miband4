#!/usr/bin/env python3
from __future__ import print_function
from datetime import datetime
import pandas as pd
import numpy as np
import time
import logging
from threading import Thread
from miband import miband
from datetime import datetime
from bluepy.btle import BTLEDisconnectError
from bluepy.btle import Scanner, Peripheral, Characteristic, ScanEntry, UUID
from bluepy import btle
import schedule as s
import pymongo
import matplotlib.pyplot as plt
scanner = Scanner()
frames = []
addr_auth = [['f8:58:1d:1d:d3:b7','D50271FC8E0AA5E0BE7CFCD27F7AE336'],['f0:96:ca:e3:92:c2','FDC91E5E86196E7AADAA924F2F3A66F5'],
             ['df:2c:42:3b:86:a1','14AA302ADFE521233D46B70725FB5C2A'],['d2:c0:c8:21:1d:ff','3E3A547592A768D2A6010547168C1F7B']]
result = pd.DataFrame(columns=['DEV_ADDR','DEV_RSSI','HR'])
#addr_auth = [['f8:58:1d:1d:d3:b7','D50271FC8E0AA5E0BE7CFCD27F7AE336']]

n_dev = len(addr_auth)

class Battiti1(Thread):

    def __init__(self,mac_address,auth_key,debug=True):
        FORMAT = '%(asctime)-15s %(name)s (%(levelname)s) > %(message)s'
        logging.basicConfig(format=FORMAT)
        log_level = logging.WARNING if not debug else logging.DEBUG
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.setLevel(log_level)

        Thread.__init__(self)
        self.mac_address = mac_address
        self.auth_key  = bytes.fromhex(auth_key)
        self.heart_rate_list = []



    def heart_logger(self, data):
        self.heart_rate_list.append(data)
        print(datetime.now(), " MAC_ADDRESS:",self.mac_address,' Realtime heart BPM:', self.heart_rate_list)


    def run(self):
        success = False
        while not success:
            try:
                if (self.auth_key):
                    band = miband(self.mac_address, self.auth_key, debug=True)
                    success = band.initialize()
                else:
                    band = miband(self.mac_address, debug=True)
                    success = True
                break
            except BTLEDisconnectError:
                print('Connection to the MIBand failed. Trying out again in 3 seconds')
                time.sleep(3)
                continue
            except KeyboardInterrupt:
                print("\nExit.")
                exit()

        band.start_heart_rate_realtime(heart_measure_callback=self.heart_logger)

        heart_list = self.heart_rate_list
        self.heart_rate_list = []
        self._log.info(heart_list)

        band.disconnect()

#END CLASS

#MAIN

"""
devs = scanner.scan(1);
res = np.array([(datetime.now(), dev.getValueText(btle.ScanEntry.COMPLETE_LOCAL_NAME),
                 dev.getValueText(btle.ScanEntry.SHORT_LOCAL_NAME), dev.addr, dev.addrType, dev.connectable,
                 dev.rssi, 0) for dev in devs])
df = pd.DataFrame(res, columns=['DATETIME', 'COMPL_LOC_NAME', 'SHORT_LOC_NAME', 'DEV_ADDR', 'DEV_ADDR_TYPE',
                                'DEV_CONNECTABLE', 'DEV_RSSI', 'HR'])
addr_rssi = df[df['COMPL_LOC_NAME'] == 'Mi Smart Band 4'][['DEV_ADDR', 'DEV_RSSI']]
mac_array = list(np.unique(list(addr_rssi['DEV_ADDR'])))
n_mac = len(mac_array)
"""
def misurazioni():
    df = pd.read_pickle("scan.pkl")
    addr_rssi = df[df['COMPL_LOC_NAME'] == 'Mi Smart Band 4'][['DEV_ADDR', 'DEV_RSSI','HR']]
    mac_array = list(np.unique(list(addr_rssi['DEV_ADDR'])))
    n_mac = len(mac_array)
    threads = []
    hr_results =  []
    rssi_lst = []
    auth_mac_address=[]
    i = 0
    j = 0
    for i in range(n_mac):
        mac_address = mac_array[i]
        for j in range(n_dev):
            if mac_address == addr_auth[j][0]:
                auth_mac_address.append(addr_auth[j][0])
                auth_key = addr_auth[j][1]
                rssi = addr_rssi[addr_rssi['DEV_ADDR'] == mac_address][['DEV_ADDR', 'DEV_RSSI']]
                t = Battiti1(mac_address,auth_key)
                hr_results.append(t.heart_rate_list)

                threads.append(t)


    # Launch all threads
    for t in threads:
        t.start()
    for t in threads:
        t.join()


    rssi_sel=addr_rssi[addr_rssi["DEV_ADDR"].isin(auth_mac_address)].reset_index(drop=True)
    rssi_sel["HR"]=[np.array(l).mean() for l in hr_results]
    print('rssi_sel',rssi_sel)
    hr_db = rssi_sel.to_json(orient='records')
    #print(hr_db)
    config = {"host": "10.8.9.27", "token": "TFyCMKn7IOl0JhYUk1J0"}

    # Open MongoDB
    myclient = pymongo.MongoClient("mongodb://{}:27017/".format(config["host"]))
    mydb = myclient["BLE_scanner"]
    # mycol = mydb["pycom_solar"] #collection first experiment
    # mycol = mydb["pycom_solar_2"] #collection second experiment (battery voltage + solar panel voltage from ADC)
    mycol = mydb["hr_detection"]  # collection new ADC acquistion + machine Temperature + v_solar stats

    #x = mycol.insert_many(hr_db)
    data = {hr_db: hr_db}
    result = mycol.insert_one(data).inserted_id

s.every(5).seconds.do(misurazioni)

while True:
    s.run_pending()
    time.sleep(1)
