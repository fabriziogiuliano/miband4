
#!/usr/bin/env python3
#from datetime import datetime
#import csv
import pandas as pd
import numpy as np
from bluepy import btle
from bluepy.btle import Scanner, Peripheral, Characteristic, ScanEntry, UUID
import time
import miband4_lib as mib
import logging
from threading import Thread
#scanner = Scanner()
#frames = []
#hr = []
#heart = []
#result = pd.DataFrame(columns=['DEV_ADDR','DEV_RSSI','HR'])
logging.basicConfig(level=logging.INFO, file='sample.log')
#logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

class Battiti1(Thread):
    hr = []
    def __init__(self,mac_address,auth_key):
        Thread.__init__(self)
        self.mac_address = mac_address
        self.auth_key = auth_key
    def run(self):
        mac_address = self.mac_address
        auth_key = self.auth_key
        hr = mib.run(mac_address,auth_key)
        time.sleep(0.5)

t1 = Battiti1('f8:58:1d:1d:d3:b7','D50271FC8E0AA5E0BE7CFCD27F7AE336')
t2 = Battiti1('f0:96:ca:e3:92:c2','FDC91E5E86196E7AADAA924F2F3A66F5')

t1.start()
time.sleep(0.2)
t2.start()