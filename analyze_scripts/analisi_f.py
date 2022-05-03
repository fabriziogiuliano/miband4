import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("pippo_last.csv", low_memory=False)


#df[df["COMPL_LOC_NAME"]=="Mi Smart Band 4"]["DEV_ADDR"]

#f8:58:1d:1d:d3:b7

#mac_addr_list=["f8:58:1d:1d:d3:b7","f0:96:ca:e3:92:c2","ff:46:0f:1d:d8:51"]
#mac_addr_list=["f8:58:1d:1d:d3:b7","f0:96:ca:e3:92:c2"]
mac_addr_list=["f8:58:1d:1d:d3:b7"]
df['DATETIME'] = pd.to_datetime(df['DATETIME'])
#print("calma calma calma...")
datetime=[]
rssi=[]
rssi_dev= []
rssi_mean=[]
rssi_std=[]
#n=165000
#j = df.shape[0]
j = 1500

for mac_addr in mac_addr_list: 
    #datetime_dev = df[df["DEV_ADDR"]==mac_addr]["DATETIME"]
    datetime.append(df[df["DEV_ADDR"]==mac_addr]["DATETIME"])
    rssi.append(df[df["DEV_ADDR"]==mac_addr]["DEV_RSSI"])
    inizio = df[df["DEV_ADDR"]==mac_addr]["DATETIME"].iloc[0]
    #a = df.loc[(df.DEV_ADDR == mac_addr) & (df.DATETIME <= df['DATETIME'].iloc[100]) & (df.DATETIME >= df['DATETIME'].iloc[30])]["DEV_RSSI"]
    #print(a)
        
    #print(rssi_dev)
        
    l = len(datetime)
    #TODO: Stats analysis
    #rssi_dev.append(df['DEV_RSSI'].iloc[1])
    df_dev = df[df.DEV_ADDR == mac_addr]
    df_dev = df_dev.set_index('DATETIME')
    rssi_mean_dev = df_dev.groupby([pd.Grouper(freq='10Min')])["DEV_RSSI"].mean()
    rssi_std_dev = df_dev.groupby([pd.Grouper(freq='10Min')])["DEV_RSSI"].std()
    print("qui")
    #TODO: isolate stats for MAC address
    #Plot for different MAC address


    """
    for n in range(j):
        fine = df[df["DEV_ADDR"]==mac_addr]["DATETIME"].iloc[n]        
        delta = ((fine-inizio).total_seconds())/60

        if (delta>=0.5):
            print(delta)
            df_dev = df[df.DEV_ADDR == mac_addr]
            df_dev.groupby([pd.Grouper(freq='1Min')])["DEV_RSSI"].mean()


            #rssi_dev.append(df_dev[(df.DATETIME <= fine) & (df.DATETIME > inizio)]["DEV_RSSI"].mean())


            
            print(rssi_dev)


            rssi_mean.append(np.array(rssi_dev).mean())
            rssi_std.append(np.array(rssi_dev).std())

            inizio = df[df["DEV_ADDR"]==mac_addr]["DATETIME"].iloc[n]

    
    """
#print(mean,var)

plt.plot(rssi_mean,label="RSSI mean"); plt.plot(rssi_std,label="RSSI std");plt.legend()


f, (ax1, ax2) = plt.subplots(1, 2)

#fig, axs = plt.subplots(2)
   
for i in range(0,len(mac_addr_list)):
    ax1.plot(datetime[i],rssi[i],label="dev_addr={}".format(mac_addr_list[i])) 

ax2.plot(rssi_mean,rssi_std,'.')

ax1.set(xlabel="time",ylabel="RSSI [dBm]")
#ax1.ylabel="RSSI [dBm]"
ax1.legend()
ax2.set(xlabel="mean",ylabel="MSE")
#ax2.ylabel="MSE"

plt.show()