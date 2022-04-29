import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("pippo_last.csv", low_memory=False)


#df[df["COMPL_LOC_NAME"]=="Mi Smart Band 4"]["DEV_ADDR"]

#f8:58:1d:1d:d3:b7

mac_addr_list=["f8:58:1d:1d:d3:b7","f0:96:ca:e3:92:c2","ff:46:0f:1d:d8:51"]
df['DATETIME'] = pd.to_datetime(df['DATETIME'])
print("calma calma calma...")


datetime=[]
rssi=[]
for mac_addr in mac_addr_list:

    datetime.append(df[df["DEV_ADDR"]==mac_addr]["DATETIME"])
    rssi.append(df[df["DEV_ADDR"]==mac_addr]["DEV_RSSI"])
    #TODO: Stats analysis

for i in range(0,len(mac_addr_list)):
    plt.plot(datetime[i],rssi[i],label="dev_addr={}".format(mac_addr_list[i]))

plt.xlabel="time"
plt.ylabel="RSSI [dBm]"
plt.legend()
plt.show()




