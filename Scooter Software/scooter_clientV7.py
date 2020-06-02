import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import MFRC522
import serial
import pynmea2
import concurrent.futures
import time
import json
import string

from m365py import m365py
from m365py import m365message

class Lock_status:

    l = True

    def print_status():
        print(Lock_status.l)

    def unlock(check):
        if check == 1:
            Lock_status.l = True
        else:
            Lock_status.l = False

def on_message(client, userdata, msg):

    topic = msg.topic
    content = msg.payload.decode()
    print(topic)
    print(content)
    
    if topic == "trotinete/1/cardanswer":
        if content == "ok":
            Lock_status.unlock(0)
        elif content == "nok":
            Lock_status.unlock(1)

    if topic == "trotinete/1/geolock":
        if content == "lock":
            Lock_status.unlock(1)
        elif content == "unlock":
            Lock_status.unlock(0)

# GLOBAL VARS
# Libraries vars
# Broker connection - MQTT
client = mqtt.Client()
#Put the  ip of your broker
client.connect("0.0.0.0",1883)
client.subscribe("trotinete/1/cardanswer")
client.subscribe("trotinete/1/geolock")
client.on_message = on_message
client.loop_start()
# Create an object of the class MFRC522 - RFID
Reader = MFRC522.MFRC522()

# callback for received messages from scooter
def handle_message(m365_peripheral, m365_message, value):
    print('Received message => {}'.format(json.dumps(value, indent=4)))

    # check for specific message
    if m365_message.attribute == m365message.Attribute.BATTERY_VOLTAGE:
        print('Battery voltage {} V'.format(value['battery_voltage']))

    if m365_message.attribute == m365message.Attribute.SUPPLEMENTARY:
        if value['kers_mode'] == m365py.KersMode.WEAK:
            print('kers set to weak')

def connected(m365_peripheral):
    print('Scooter Connected')

def disconnected(m365_peripheral):
    print('Scooter Disconnected')

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("trotinete/1/cardanswer")
    client.subscribe("trotinete/1/geolock")

def unlock():
    scooter.request(m365message.turn_off_lock)
    scooter.request(m365message.turn_on_tail_light)
    scooter.request(m365message.tail_light_status)

def lock():
    scooter.request(m365message.turn_on_lock)
    scooter.request(m365message.turn_off_tail_light)
    scooter.request(m365message.tail_light_status)

def rfid_read():
    while True:
        # Scan for cards
        (status,TagType) = Reader.MFRC522_Request(Reader.PICC_REQIDL)
        # Get the UID of the card
        (status,uid) = Reader.MFRC522_Anticoll()
        # If we have the UID, continue
        if status == Reader.MI_OK:
            # store uid
            card_id = ''
            for id in uid:
                card_id += str(id)

            if card_id != '':
                client.publish("trotinete/1/cardrequest", card_id)
            time.sleep(5)
        # Prevent from sending card id several times in a row
        # time.sleep(1)
    return "RFID module terminated"

def gps():
    while True:
        port="/dev/ttyAMA0"
        ser=serial.Serial(port, baudrate=9600, timeout=0.5)
        newdata=ser.readline()
        if "$GPRMC" in str(newdata):
            try:
                a = newdata.decode('utf-8')
                newmsg=pynmea2.parse(a)
                lat=newmsg.latitude
                lng=newmsg.longitude
                gps =str(lng) + "," + str(lat)
                client.publish("trotinete/1/location", gps)
                print(gps)
            except:
                continue

    return "GPS module terminated"

def scooter_control():
    # This is the Scooter - Bluetooth
    #put the mac address of your scooter
    scooter_mac_address = 'E3:15:58:36:C0:90'
    scooter = m365py.M365(scooter_mac_address, handle_message)
    scooter.set_connected_callback(connected)
    scooter.set_disconnected_callback(disconnected)
    scooter.connect()
    scooter.request(m365message.battery_percentage)
    scooter.request(m365message.turn_on_lock)

    while True:
        
        if Lock_status.l==True:
            scooter.request(m365message.turn_off_tail_light)
            scooter.request(m365message.turn_on_lock)
            print("lockei")
        else:
            scooter.request(m365message.turn_off_lock)
            scooter.request(m365message.turn_on_tail_light)
            print("deslockei")

        
        scooter.request(m365message.battery_percentage)
        data = json.dumps(scooter.cached_state, indent=4, sort_keys=True)
        battery = json.loads(data)
        client.publish("trotinete/1/battery",  str(battery['battery_percent']))
        # Send battery status every 5s
        time.sleep(3)
    return "main terminated"

def keep_alive():

    while True:
        if Lock_status.l==False:
            print("do nothing")
        else:
            print("passei aqui")
            Lock_status.unlock(0)
            time.sleep(3)
            Lock_status.unlock(1)
            time.sleep(3600)

        time.sleep(15)

try:
    # Threads
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(rfid_read)
        executor.submit(gps)
        executor.submit(scooter_control)
        executor.submit(keep_alive)



except KeyboardInterrupt:
    print("keyboard interrupt\n")
except:
    print("unknown error\n")
finally:
    # Calls Client disconnect
    client.disconnect()
    # Calls GPIO cleanup
    GPIO.cleanup()