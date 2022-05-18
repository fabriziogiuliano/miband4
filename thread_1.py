
#!/usr/bin/env python3
#from datetime import datetime
#import csv
import pandas as pd
import numpy as np
from bluepy import btle
from bluepy.btle import Scanner, Peripheral, Characteristic, ScanEntry, UUID
import time
from miband4_lib import Miband4_lib
import logging
from threading import Thread

from miband import miband
from datetime import datetime

from bluepy.btle import BTLEDisconnectError

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


#TODO: ADD SCAN HERE!! :-)


t1 = Battiti1('f8:58:1d:1d:d3:b7','D50271FC8E0AA5E0BE7CFCD27F7AE336')
t2 = Battiti1('f0:96:ca:e3:92:c2','FDC91E5E86196E7AADAA924F2F3A66F5')

t1.start()
time.sleep(0.2)
t2.start()