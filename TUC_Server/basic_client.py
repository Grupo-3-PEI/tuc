import paho.mqtt.client as mqtt
import time
import json
import csv
#import server_client

def on_message(client, userdata, msg):
    
    topic = msg.topic
    content = msg.payload.decode()
    print(topic)
    print(content)

def check_id(id):                               # Checks if scooter exists on file
    with open("static/scooters.csv",'r') as csv_file:        
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for scooter in csv_reader:
            if scooter[0] == id:
                return True

while True:
    client = mqtt.Client()                      # Connect to MQTT server
    # client.connect("192.168.1.7",1883)
    client.connect("77.54.68.192",1883)
    print("Insert the command\n")
	
    option = input()
    # print(option)
    print(check_id(option))
    if check_id(str(option)):
        publish_str = "trotinete/"+str(option)+"/cardanswer"
        print(publish_str)
        client.publish(publish_str, "nok")


    
    
