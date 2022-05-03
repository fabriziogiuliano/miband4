import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("pippo_last.csv", low_memory=False)

#df[df["COMPL_LOC_NAME"]=="Mi Smart Band 4"]["DEV_ADDR"]

mac_addr_list=["f8:58:1d:1d:d3:b7","f0:96:ca:e3:92:c2","ff:46:0f:1d:d8:51"]
#mac_addr_list=["f8:58:1d:1d:d3:b7","f0:96:ca:e3:92:c2"]

#mac_addr_list=["f8:58:1d:1d:d3:b7"]

df['DATETIME'] = pd.to_datetime(df['DATETIME'])
datetime=[]
rssi=[]
rssi_dev= []
rssi_mean=[]
rssi_std=[]
media=[]
dev=[]

for mac_addr in mac_addr_list:
 
    #datetime_dev = df[df["DEV_ADDR"]==mac_addr]["DATETIME"]
    datetime.append(df[df["DEV_ADDR"]==mac_addr]["DATETIME"])
    rssi.append(df[df["DEV_ADDR"]==mac_addr]["DEV_RSSI"])
    #print(rssi)
    df_dev = df[df.DEV_ADDR == mac_addr] 
    

    #print(a)
    df_dev = df_dev.set_index('DATETIME')
    #df_dev = df_dev.groupby('DEV_ADDR')
    rssi_mean_dev = df_dev.groupby([pd.Grouper(freq='2Min')])["DEV_RSSI"].mean()
    media.append(rssi_mean_dev)
    rssi_std_dev = df_dev.groupby([pd.Grouper(freq='2Min')])["DEV_RSSI"].std()
    dev.append(rssi_std_dev)
    #TODO: isolate stats for MAC address
    #Plot for different MAC address

#print(mean,var)
for i in range(0,len(mac_addr_list)):
    plt.plot(datetime[i],rssi[i],label="dev_addr={}".format(mac_addr_list[i]))
#rssi_mean_dev.plot(label="rssi mean") 
#rssi_std_dev.plot(label="rssi std")
    plt.plot(media[i],label='mean_dev{}'.format(mac_addr_list[i]))
    plt.plot(dev[i],label='stdev_dev{}'.format(mac_addr_list[i]))
    plt.legend()
plt.show()
"""
plt.plot(rssi_mean,label="RSSI mean") 
plt.plot(rssi_std,label="RSSI std")
plt.legend()
plt.show()


f, (ax1, ax2) = plt.subplots(1, 2)

#fig, axs = plt.subplots(2)
   
for i in range(0,len(mac_addr_list)):
    ax1.plot(datetime[i],rssi[i],label="dev_addr={}".format(mac_addr_list[i])) 

ax2.plot(rssi_mean)
ax2.plot(rssi_std)

ax1.set(xlabel="time",ylabel="RSSI [dBm]")
#ax1.ylabel="RSSI [dBm]"
ax1.legend()
ax2.set(xlabel="mean",ylabel="MSE")
#ax2.ylabel="mean,stdev"
plt.show()
"""

