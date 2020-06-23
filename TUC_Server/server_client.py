import paho.mqtt.client as mqtt
import init
import csv
import os
import math
from datetime import datetime
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class Scooter:                      # Scooter's class
    def __init__(self,id):
        self.id = id
        self.get_state()

    def get_state(self):            # Initialize the scooter attributes by reading the scooter.csv
        with open("static/scooters.csv",'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)
            for scooter in csv_reader:
                if scooter[0] == self.id:       # Get the file row with this scooter's id
                    self.state = scooter[1]
                    self.battery = scooter[2]
                    self.user = scooter[3]
                    self.location = scooter[4]
                    self.geofencing = scooter[5]
            

    def update_scooter(self,id):        # Update the scooter's information
        self.state = id
        temp_user = 0
        if id != 0:
            temp_user = self.user
     
        update_scooters(self.id,self.state,self.battery,temp_user,self.location,self.geofencing)


class User:                             # User's class
    def __init__(self,id,name,email):
        self.id = id
        self.name = name
        self.email = email

    

############################ Scooters CSV #############################################################
def check_id(id):                               # Checks if scooter exists on file
    with open("static/scooters.csv",'r') as csv_file:        
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for scooter in csv_reader:
            if scooter[0] == id:
                return True

def insert_scooter(id,status,battery,user,location,geofencing):    # Insert a new scooter on the file
    scooter = [id,status,battery,user,location,geofencing]
    with open('static/scooters.csv','a') as csv_file:
        csv_write = csv.writer(csv_file,delimiter=',')
        csv_write.writerow(scooter)

def update_scooters(id,status,battery,user,location,geofencing):   # Update the csv scooter file with the new information
    up_scooter = [id,status,battery,user,location,geofencing]
    if id not in get_ids():
        return None
    with open("static/scooters.csv",'r') as file_reader, open("static/scooters_temp.csv",'w') as file_writer:
        csv_reader = csv.reader(file_reader)
        csv_write = csv.writer(file_writer,delimiter=',')
        for scooter in csv_reader:
            if scooter[0] == id:
                csv_write.writerow(up_scooter)
            else:
                csv_write.writerow(scooter)

    os.remove("static/scooters.csv")
    os.rename("static/scooters_temp.csv","static/scooters.csv")

def get_ids():                              # Return a list with all the scooters's id
    all_ids = []
    with open("static/scooters.csv",'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for card in csv_reader:
            all_ids.append(card[0])
    return all_ids

############################ Scooters USE #############################################################
def is_full(id):
    count = 0
    with open("static/scooter_use.csv",'r') as file_reader:
        csv_reader = csv.reader(file_reader)
        for scooter in csv_reader:
            if scooter[0] == id:
                count += 1
    if(count >= 20):
        return True
    return False

def save_unlock(id_trot, id_user):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M")
    use = [id_trot,dt_string,"in_use",id_user]
    if is_full(id_trot):
        with open("static/scooter_use.csv",'r') as file_reader, open("static/scooter_use_temp.csv",'w') as file_writer:  
            csv_reader = csv.reader(file_reader)
            csv_write = csv.writer(file_writer,delimiter=',')
            is_found = False
            for scooter in csv_reader:
                if not scooter[0] == id_trot or not is_found == False:
                    csv_write.writerow(scooter)
                else:
                    is_found = True
            csv_write.writerow(use)
            os.remove("static/scooter_use.csv")
            os.rename("static/scooter_use_temp.csv","static/scooter_use.csv")
    else:
        with open("static/scooter_use.csv",'a') as csv_file:
            csv_writer = csv.writer(csv_file,delimiter=',')
            csv_writer.writerow(use)

def save_lock(id):
    with open("static/scooter_use.csv",'r') as file_reader, open("static/scooter_use_temp.csv",'w') as file_writer:
        csv_reader = csv.reader(file_reader)
        csv_write = csv.writer(file_writer,delimiter=',')
        for scooter in csv_reader:
            if scooter[0] == id and scooter[2] == "in_use":
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M")
                use = [id,scooter[1],dt_string,scooter[3]]
                csv_write.writerow(use)
            else:
                csv_write.writerow(scooter)
    
    os.remove("static/scooter_use.csv")
    os.rename("static/scooter_use_temp.csv","static/scooter_use.csv")

######################################## People CSV ####################################################
def insert_user(id,name,email):                 # Insert a user on the people.csv file
    user = [id,name,email]
    with open('static/people.csv','a') as csv_file:
        csv_write = csv.writer(csv_file,delimiter=',')
        csv_write.writerow(user)

def update_users(id,name,email):                # Update the people.csv file with new information
    up_user = [id,name,email]
    if id not in get_user_ids():
        return None
    with open("static/people.csv",'r') as file_reader, open("static/people_temp.csv",'w') as file_writer:
        csv_reader = csv.reader(file_reader)
        csv_write = csv.writer(file_writer,delimiter=',')
        for user in csv_reader:
            if user[0] == id:
                csv_write.writerow(up_user)
            else:
                csv_write.writerow(user)

    os.remove("static/people.csv")
    os.rename("static/people_temp.csv","static/people.csv")

def get_user_ids():                     # Return a list with all the ids of the users
    all_ids = []
    with open("static/people.csv",'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for card in csv_reader:
            all_ids.append(card[0])
    return all_ids

########################################## Geofencing ##################################################
def write_location():
    location_json = '{"type":"FeatureCollection","features":['
    with open("static/scooters.csv",'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for scooter in csv_reader:
            coordinates = scooter[4].replace('"','')
            location_json += '{"type":"Feature","properties":{"name":"TUC' + scooter[0] + '","status":"' + scooter[1] + '","battery":"' + scooter[2] + '"},"geometry":{"type":"Point","coordinates":[' + coordinates + "]}}"
            if scooter[0] != get_last_id():
                location_json += ","
            else:
                location_json += "]}"   
    f = open("static/map1.geojson","w")
    f.write(location_json)
    f.close()

def get_last_id():
    return get_ids()[len(get_ids())-1]

def is_inside_geofencing(location):
    coordinates = location.replace('"','')
    coordinates = coordinates.split(",")
    points = get_GeofencingPoints()
    p1 = Point(float(coordinates[0]),float(coordinates[1]))
    polygon = Polygon(points)
    if polygon.contains(p1):
        return True
    return False

def get_GeofencingPoints():
    points = []
    with open("static/geofencing.csv",'r') as file_reader:
        csv_reader = csv.reader(file_reader)
        next(csv_reader)
        for point in csv_reader:
            p = Point(float(point[0]),float(point[1]))
            points.append(p)
    return points

########################################### MQTT #####################################################
def on_connect(client, userdata, flags, rc):            
    print("Connected with result code "+str(rc))   
    print(get_ids())
    for id in get_ids():                            # Iterate over all the scooters's id to subscribe to all possible topics
        sub_string_battery = "trotinete/"+id+"/battery"
        sub_string_location = "trotinete/"+id+"/location"
        sub_string_cardrequest = "trotinete/"+id+"/cardrequest"
        sub_string_card = "trotinete/"+id+"/card"
        sub_string_insertcard = "trotinete/"+id+"/insertcard"
        client.subscribe(sub_string_battery)
        client.subscribe(sub_string_location)
        client.subscribe(sub_string_cardrequest)
        client.subscribe(sub_string_card)
        client.subscribe(sub_string_insertcard)
        print(sub_string_battery)
        print(sub_string_location)
        print(sub_string_cardrequest)
        print(sub_string_card)
        print(sub_string_insertcard)

def on_message(client, userdata, msg):
    
    topic = msg.topic
    content = msg.payload.decode()
    print(topic)
    print(content)
    print("####")
    
    for id in get_ids():                                # Iterate over all scooters ID, to find the ones that are trying to communicate
        topic_cardrequest = "trotinete/"+id+"/cardrequest"
        topic_battery = "trotinete/"+id+"/battery"
        topic_location = "trotinete/"+id+"/location"


        trot = Scooter(id)
        

            # Check topics
        if topic == topic_cardrequest:                              # Insert card          
            if check_id(id) == True and content in get_user_ids():  # Check if scooter and users exist
                print("ID correto")
                print(trot.state)
                print(trot.geofencing)
                if int(id) == int(trot.state) and trot.user == content: # Check if the scooter is already unlocked and if the user trying to lock is the one who unlocked it
                    trot.update_scooter(0)
                    print("Locked")
                    save_lock(id)
                    publish_str = "trotinete/"+id+"/cardanswer"
                    client.publish(publish_str, "nok")
                elif int(trot.state) == 0 and trot.geofencing == "INSIDE":                               # Check if the scooter is locked 
                    trot.user = content
                    trot.update_scooter(int(id))
                    print("Unlocked")
                    save_unlock(id,content)
                    publish_str = "trotinete/"+id+"/cardanswer"
                    client.publish(publish_str, "ok")
            else:       
                if check_id(id) == False:
                    print("That scooter doesn't exist.")
                elif content not in get_user_ids():
                    print("This user does not have permission.")
            break
        elif topic == topic_battery:                        # Update battery
            if check_id(id) == True:
                trot.battery = content
                update_scooters(id,trot.state,trot.battery,trot.user,trot.location,trot.geofencing)
            break 
        elif topic == topic_location:                       # Update location
            if check_id(id) == True and content != "0.0,0.0":
                trot.location = content
                if not is_inside_geofencing(content) :
                    trot.state = 0
                    trot.geofencing = "OUTSIDE"
                    print("Scooter out of range")
                    str_pub = "trotinete/"+id+"/cardanswer"
                    save_lock(id)
                    client.publish(str_pub, "nok")
                else:
                    trot.geofencing = "INSIDE"
                    print("Inside geofencing")
                update_scooters(id,trot.state,trot.battery,trot.user,trot.location,trot.geofencing)
                write_location()

            break 


client = mqtt.Client()                      # Connect to MQTT server
# client.connect("192.168.1.7",1883)
client.connect("77.54.68.192",1883)

client.on_connect = on_connect
client.on_message = on_message
client.loop_forever()



