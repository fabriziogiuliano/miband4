#!/usr/bin/env python3
from __future__ import print_function
import pandas as pd
pd.options.mode.chained_assignment = None 
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
import matplotlib
matplotlib.use('Agg')
from LidarUtils.LidarDataProcess import LidarDataProcess
import logging, sys
from time import sleep
logLevel=logging.DEBUG
logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
import numpy as np
np.set_printoptions(formatter={'int':hex})
import time

import sys, getopt

N_SEC=60 #number of sectors
T_scan=3
T_LoRA=10
MAX_LORA_SIZE=244
EN_RPI_LORA=True
scanner = Scanner(1)
frames = []
addr_auth = [['f8:58:1d:1d:d3:b7','D50271FC8E0AA5E0BE7CFCD27F7AE336'],['f0:96:ca:e3:92:c2','FDC91E5E86196E7AADAA924F2F3A66F5'],
             ['df:2c:42:3b:86:a1','14AA302ADFE521233D46B70725FB5C2A'],['d2:c0:c8:21:1d:ff','3E3A547592A768D2A6010547168C1F7B']]
result = pd.DataFrame(columns=['DATETIME','DEV_ADDR','DEV_RSSI','HR'])

n_dev = len(addr_auth)
def lorawan_join():
    D_conf = DraginoConfig("dragino.ini")
    if D_conf.get_fcount()>=65535: #rollup rejoin
        D_conf.logger.warning("================ Unable to read session details")
        D_conf.resetJoinConfig()
    D = Dragino("dragino.ini", logging_level=logLevel)
    D.join()
    while not D.registered():
        logging.debug("Waiting for JOIN ACCEPT")
        sleep(2)
    return D, D_conf


if EN_RPI_LORA:
    import RPi.GPIO as GPIO
    from dragino import Dragino
    from dragino import DraginoConfig

    GPIO.setwarnings(False)
    D, D_conf = lorawan_join()

def sensor_loop(path=0, n_sec=N_SEC):
    while True:

        if EN_RPI_LORA:

            #pippo_list = [0x1, 0x2, 0x3]
            #D.send_bytes(pippo_list)
            l = len(data_to_send)
            for i in range(l):
                D.send_bytes(data_to_send[i])
            #D.send_bytes(sending)
                while D.transmitting:
                     pass
        else:
            logging.debug("==================================")
            logging.debug("here we send LoRa packet - SANDBOX")
            logging.debug("==================================")
            # logging.info("features={}".format(feat))

        time.sleep(T_LoRA)

import threading



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
        if data >= 0:
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
def misurazioni():

    do_scan=True
    if do_scan:
        devs = scanner.scan(T_scan);
        res = np.array([(datetime.now(), dev.getValueText(btle.ScanEntry.COMPLETE_LOCAL_NAME),
            dev.getValueText(btle.ScanEntry.SHORT_LOCAL_NAME), dev.addr, dev.addrType, dev.connectable,
            dev.rssi, 0) for dev in devs])
        df = pd.DataFrame(res, columns=['DATETIME', 'COMPL_LOC_NAME', 'SHORT_LOC_NAME', 'DEV_ADDR', 'DEV_ADDR_TYPE','DEV_CONNECTABLE', 'DEV_RSSI', 'HR'])
        print(df)
        addr_rssi = df[df['COMPL_LOC_NAME'] == 'Mi Smart Band 4'][['DATETIME','DEV_ADDR', 'DEV_RSSI']]
        mac_array = list(np.unique(list(addr_rssi['DEV_ADDR'])))
        n_mac = len(mac_array)
    else:
        df = pd.read_pickle("scan.pkl")
        addr_rssi = df[df['COMPL_LOC_NAME'] == 'Mi Smart Band 4'][['DATETIME','DEV_ADDR', 'DEV_RSSI','HR']]
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
    sending = []
    mac_addr_in_byte = []
    #mac_addr_in_hex = []
    rssi_sel['DEV_ADDR'] = list(rssi_sel['DEV_ADDR'])
    t = rssi_sel['DEV_ADDR'].shape[0]
    s = int(rssi_sel.shape[1])
    rssi_sel['HR'] = rssi_sel['HR'].fillna(0)
    for j in range(t):
        mac_addr_in_byte = []
        mac_addr_in_byte.extend([ bytearray.fromhex(m)[0] for m in rssi_sel['DEV_ADDR'].iloc[j].split(sep=':')])
        sending.extend(mac_addr_in_byte)

        rssi= int(rssi_sel['DEV_RSSI'].iloc[j])
        sending.extend([rssi*(-1)])
        hr = int(rssi_sel['HR'].iloc[j])
        sending.extend([hr])
    sending2 = []
    n_byte = len(sending)
    global data_to_send
    data_to_send = []
    if n_byte>51:
        n = n_byte - 51
        sending = sending[:51]
        sending2.extend(sending[-(n):])

        data_to_send.append(sending)
        data_to_send.append(sending2)
    else:
        data_to_send.append(sending)
        '''
        mac_addr_in_byte.extend([ bytearray.fromhex(m)[0] for m in rssi_sel['DEV_ADDR'].iloc[i].split(sep=':')])
        #mac_addr_in_hex.extend([hex(j) for j in mac_addr_in_byte])
    sending.extend(mac_addr_in_byte)
    
    
    rssi_sel['DEV_RSSI'] = rssi_sel['DEV_RSSI'].astype(int)
    #rssi_sel['DEV_RSSI'] = rssi_sel['DEV_RSSI'].apply(lambda x: hex(x))
    sending.extend(-1*(rssi_sel['DEV_RSSI']))

    rssi_sel['HR'] = (rssi_sel['HR'].fillna(0)).astype(int)
    #rssi_sel['HR'] = rssi_sel['HR'].apply(lambda x: hex(x))
    sending.extend((rssi_sel['HR']))
    sending2 = []
    n_byte = len(sending)
    global data_send
    data_send = []
    if n_byte>51:
        n = n_byte - 51
        sending = sending[:51]
        data_send.append(sending)
        sending2.extend(sending[-(n):])
        data_send.append(sending2)
    else:
        data_send.append(sending)
    #hr_db = rssi_sel
    #hr_db.append(rssi_sel)
    '''
    n_scans = 50
    N_SEC = 60  # number of sectors

    T_LoRA = 10
    MAX_LORA_SIZE = 244
    EN_RPI_LORA = True
    argv = sys.argv[1:]
    help_str = '{} -f <num_feat_sectors> -s <num_init_scans> -t <lora_interpacket>\n' \
               '--------------------------------------------------------------------------\n' \
               'num_feat_sectors: \tnumber of Lidar samples to be send via LoRa Link\n' \
               'num_init_scans: \tnumber of initial environment scan\n' \
               't_lorainterpacket: \ttime between to lora transmissions\n' \
               '--------------------------------------------------------------------------\n' \
               ''.format(sys.argv[0])

    try:
        opts, args = getopt.getopt(argv, "hf:s:t:", ["num_feat_sectors=", "num_init_scans=", "lora_interpacket="])
    except getopt.GetoptError:
        print(help_str)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(help_str)
            sys.exit()
        elif opt in ("-f", "--num_feat_sectors"):
            N_SEC = int(arg)
        elif opt in ("-s", "--num_init_scans"):
            n_scans = int(arg)
        elif opt in ("-t", "--lora_interpacket"):
            T_LoRA = int(arg)

    if N_SEC * 4 > MAX_LORA_SIZE:
        print("WARNING: N_SEC={} is greater than {}, set N_SEC={}".format(N_SEC, MAX_LORA_SIZE, int(MAX_LORA_SIZE / 4)))
        N_SEC = int(MAX_LORA_SIZE / 4)

    print("N_SEC={}".format(N_SEC))
    print("n_scans={}".format(n_scans))
    print("T_LoRA={}".format(T_LoRA))

    t3 = threading.Thread(target=sensor_loop, args=(1,))
    t3.start()
    logging.info("Main    : all done")

    '''
    hr_db = rssi_sel.to_dict(orient='list')
    config = {"host": "10.8.9.27", "token": "TFyCMKn7IOl0JhYUk1J0"}

    # Open MongoDB
    myclient = pymongo.MongoClient("mongodb://{}:27017/".format(config["host"]))
    mydb = myclient["BLE_scanner"]
    mycol = mydb["detection_hr_rssi"]
    data = hr_db
    result = mycol.insert_one(data).inserted_id
    '''

s.every(5).seconds.do(misurazioni)

while True:
    s.run_pending()
    time.sleep(1)


