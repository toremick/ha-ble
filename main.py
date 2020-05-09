#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import time
import struct
from defs import *

#mqtt server address
broker_address="192.168.2.30"


#example data telegram 
#$GPRP,A06FAA4F74AF,CC4B7399BCB2,-87,02011A0C26FE88080101A26FAA4F74AE



def getTemp(msg):
    val_one = int(msg[24:26], 16)
    val_two = int(msg[26:28], 16)

    vals = (val_one, val_two)
    btarray = bytearray(vals)
    integer = struct.unpack('h'*(len(btarray)//2), btarray)
    temp = integer[0]/100.0
    return temp

    

def getBatt(msg):
    val_one = int(msg[18:20], 16)
    val_two = int(msg[20:22], 16)

    vals = (val_one, val_two)
    btarray = bytearray(vals)
    integer = struct.unpack('h'*(len(btarray)//2), btarray)
    temp = integer[0]/100.0
    return temp

    
def on_message(client, userdata, message):
    try:
        client.publish("ble2mqtt/state", "online")
        data = str(message.payload.decode("utf-8"))
        data = data.split(',')
        mac = data[1]
        signal = data[3]
        payload = data[4]
        senstype = payload[0:14]
        if senstype  == "02010612FF0D00":
            extra = payload[22:24]
            if extra == '01':
                button = "on"
            elif extra == '00':
                button = "off"    
            batt = getBatt(payload)
            temp = getTemp(payload)
            batt = round((float(batt)/3.3)*100, 2)
            topic = "ignics/" + str(mac) + "/"
            
            batt_cfg = battery_cfg.replace('MACADDRESS', str(mac))
            temp_cfg = temperature_cfg.replace('MACADDRESS', str(mac))
            link_cfg = signal_cfg.replace('MACADDRESS', str(mac))
            
            tpmsg = topicmsg.replace('BATT', str(batt))
            tpmsg = tpmsg.replace('TEMP', str(temp))
            tpmsg = tpmsg.replace('LINK', str(signal))
            
            
            client.publish("homeassistant/sensor/" + mac + "/battery/config", batt_cfg, retain=True)
            client.publish("homeassistant/sensor/" + mac + "/temperature/config", temp_cfg, retain=True)
            client.publish("homeassistant/sensor/" + mac + "/linkquality/config", link_cfg, retain=True)
            client.publish("ble2mqtt/" + mac, tpmsg)
                
    except Exception as e:
        print("exception: ")
        print(e)



client = mqtt.Client("ble2mqttscript")
client.connect(broker_address)
client.subscribe("tores/#")
client.publish("ble2mqtt/state", "online")
client.on_message=on_message
client.loop_forever()
