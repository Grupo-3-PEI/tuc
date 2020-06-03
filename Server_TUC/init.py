from flask import Flask, render_template, Blueprint, request, session, Response
import json
import os
import csv
import logging
import sys
#from server_client import force_lock
# logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
bp = Blueprint('auth', __name__, url_prefix='/auth')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0



@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
################################## HTTP SERVER ###########################################################
@app.route("/", methods=['POST','GET'])
def index():
    return render_template("index.html")

@app.route("/check_credentials", methods=['POST','GET'])
def check_credentials():
    if request.form['email'] == "admin" and request.form['pass'] == "admin":
        return "menu"
    
    return "false"

@app.route("/login_page")
def login_page():
    return render_template("login.html")

@app.route("/back_index")
def back_index():
    return index()

@app.route("/menu")
def menu():
	return render_template("menu.html")
@app.route("/details")
def details():
    return render_template("details.html")

@app.route("/more_info", methods=['POST','GET'])
def more_info():
    return render_template('details.html')

@app.route("/map1.geojson")
def map1():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, 'static', 'map1.geojson')
    data = json.load(open(json_url))
    return data

@app.route("/scooter_list" , methods=['POST','GET'])
def scooter_list():                              # Return a string list with all the scooters information

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    scooter_url = os.path.join(SITE_ROOT, 'static', 'scooters.csv')
    data = open(scooter_url)
    csv_reader = csv.reader(data)
        
    ids = []
    all_scooters = "" 
    next(csv_reader)
    for id_scooter in csv_reader:
        ids.append(id_scooter[0])

    data.close()

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    scooter_url = os.path.join(SITE_ROOT, 'static', 'scooters.csv')
    data = open(scooter_url)
    csv_reader = csv.reader(data)
    next(csv_reader)
    for scooter in csv_reader:
        if scooter[1] == "0":
            status_str = "AVAILABLE"
        else:
            status_str = "IN USE"
        scooter_str = ""
        scooter_str += scooter[0] + ";"
        scooter_str += status_str + ";"
        scooter_str += scooter[2] + ";"
        scooter_str += scooter[5]
        
        if scooter[0] != ids[len(ids)-1]:
            scooter_str += "\n"

        all_scooters += scooter_str
    data.close()
    return all_scooters

@app.route("/user_list")
def get_users():                              # Return a string list with all the scooters information
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    users_url = os.path.join(SITE_ROOT, 'static', 'people.csv')
    data = open(users_url)
    csv_reader = csv.reader(data)
        
    ids = []
    all_users = "HelloWorld \n" 
    next(csv_reader)
    for id_user in csv_reader:
        ids.append(id_user[0])

    data.close()

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    users_url = os.path.join(SITE_ROOT, 'static', 'people.csv')
    data = open(users_url)
    csv_reader = csv.reader(data)
    next(csv_reader)
    for user in csv_reader:
        user_str = ""
        user_str += user[0] + ";"
        user_str += user[1] + ";"
        user_str += user[2]
        
        if user[0] != ids[len(ids)-1]:
            user_str += "\n"

        all_users += user_str
    
    data.close()
    return all_users

@app.route("/delete_user", methods=['POST','GET'])
def delete_user():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    users_url_1 = os.path.join(SITE_ROOT, 'static', 'people.csv')
    data_1 = open(users_url_1)
    csv_reader = csv.reader(data_1)

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    users_url_2 = os.path.join(SITE_ROOT, 'static', 'people_write.csv')
    data_2 = open(users_url_2,'w')
    csv_writer = csv.writer(data_2)

    card = request.form['id']
    csv_writer.writerow(["id","name","email"])
    next(csv_reader)
    for user in csv_reader:
        if user[0] != card:
            csv_writer.writerow(user)

    os.remove(users_url_1)
    os.rename(users_url_2,users_url_1)

    data_1.close()
    data_2.close()
    return render_template('menu.html') 

@app.route("/add_user", methods = ['POST','GET'])
def add_user(): 
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    users_url = os.path.join(SITE_ROOT, 'static', 'people.csv')
    data = open(users_url,'a')
    csv_write = csv.writer(data)

    card = request.form['id']
    name = request.form['name']
    email = request.form['email']

    user = [card,name,email]
    csv_write.writerow(user)

    data.close()
    return render_template("menu.html")

@app.route("/get_useTime", methods = ['POST','GET'])
def get_useTime(): 
    scooter_id = 0
    scooter_id = request.form['id']

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    people_url = os.path.join(SITE_ROOT, 'static', 'people.csv')
    
    all_scooters = "" 
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    scooter_url = os.path.join(SITE_ROOT, 'static', 'scooter_use.csv')
    data = open(scooter_url)
    csv_reader = csv.reader(data)
    next(csv_reader)
    for scooter in csv_reader:
        if scooter[0] == scooter_id:
            data_3 = open(people_url)
            csv_reader_2 = csv.reader(data_3)
            next(csv_reader_2)
            for user in csv_reader_2:
                if user[0] == scooter[3]:
                    scooter_str = ""
                    scooter_str += user[0] + ";"
                    scooter_str += user[1] + ";"
                    scooter_str += scooter[1] + ";"
                    scooter_str += scooter[2] + "\n"
                    
                    all_scooters += scooter_str
            data_3.close()
    
    data.close()
    return all_scooters

@app.route("/geoFencing", methods = ['POST','GET'])
def geoFencing():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    url = os.path.join(SITE_ROOT, 'static', 'geofencing.csv')
    data = open(url,'w')
    csv_writer = csv.writer(data)
    csv_writer.writerow(["x","y"])
    coordinates = request.form.getlist('coordinates[]')
    for coordinate in coordinates:
        point = coordinate.split(",")
        csv_writer.writerow(point)

    #####################################################################################
    coords_string = ""
    location_json = '{"type":"FeatureCollection","features":['
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    url = os.path.join(SITE_ROOT, 'static', 'geomapping.geojson')
    data = open(url,'w')
    check = 0
    coordinates.append(coordinates[0])
    for coordinate in coordinates:
        coords_string += '[' + coordinate + ']'
        if coordinate != coordinates[len(coordinates)-1] or check == 0:
            coords_string += ','
        check += 1

    location_json += '{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[' + coords_string + ']]}}]}'

    data.write(location_json)
    data.close()
    return "Success"

@app.route("/geomapping.geojson")
def geomapping():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, 'static', 'geomapping.geojson')
    data = json.load(open(json_url))
    return data

#@app.route("/lock", methods = ['POST','GET'])
#def lock():
    #force_lock()
########################################################################################################################
if __name__ == "__main__":
	app.run(debug = True)

