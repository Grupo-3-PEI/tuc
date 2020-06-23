from flask import Flask
from flask_mqtt import Mqtt

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = 'mybroker.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_REFREH_TIME'] = 1.0    
mqtt = Mqtt(app)

@app.route('/')
def index():
    return "Hello World"