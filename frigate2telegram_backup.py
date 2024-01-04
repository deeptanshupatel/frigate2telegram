import paho.mqtt.client as mqtt # pip install paho.mqtt
import yaml # pip install pyyaml
import json
import logging

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logging.info("Connected to mqtt server result code: "+str(rc))
    
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("frigate/stats")
    client.subscribe("frigate/events")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    #print(msg.topic+" "+str(msg.payload))
    json_data = json.loads(msg.payload)
    logging.info(f"cam: {json_data['after']['camera']}, type: {json_data['type']}, label: {json_data['after']['label']}")

def setupLog():
    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename='frigate2telegram.log', encoding='utf-8', level=logging.DEBUG)
    logging.debug('frigate2telegram started')

def loadConfig():
    config = {}
    with open("config.yaml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logging.error(exc)
    return config

setupLog()
config = loadConfig()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(config["mqtt"]["host"], config["mqtt"]["port"])

client.loop_forever()
