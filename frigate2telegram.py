# third party imports which needs installation
import paho.mqtt.client as mqtt # pip install paho.mqtt
import yaml # pip install pyyaml

# standard imports
import json
import logging

# own classes
from telegram_helper import telegram_helper

class frigate2telegram:

    def __init__(self):
        logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename = "frigate2telegram.log", level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def onMqttConnect(self, client, userdata, flags, rc):
        try:
            self.logger.info("Connected to mqtt server result code: " + str(rc))    
            client.subscribe("frigate/events")
        except Exception as ex:
            self.logger.error(f"Exception onMqttConnect: {ex}")

    def onMqttMessage(self, client, userdata, msg):
        try:
            json_data = json.loads(msg.payload)
            event_type = json_data['type']
            event_id = json_data['after']['id']
            camera_name = json_data['after']['camera']
            motion_object = json_data['after']['label']
            self.logger.info(f"camera name: {camera_name}, event type: {event_type}, event id: {event_id}, motion object: {motion_object}")
            frigate_url = self.getFrigateUrl(event_type, event_id)
            if event_type == "new":
                self.telegram_helper.sendPhoto(frigate_url)
            elif event_type == "end":
                self.telegram_helper.sendVideo(frigate_url)
        except Exception as ex:
            self.logger.error(f"Exception onMqttMessage: {ex}")

    def getFrigateUrl(self, event_type, event_id):
        try:
            url = None
            if event_type == "new":
                url = f'http://{self.config["frigate"]["host"]}:{self.config["frigate"]["port"]}/api/events/{event_id}/snapshot.jpg?bbox=1&quality=100&timestamp=1'
            elif event_type == "end":
                url = f'http://{self.config["frigate"]["host"]}:{self.config["frigate"]["port"]}/api/events/{event_id}/clip.mp4'
            return url
        except Exception as ex:
            self.logger.error(f"Exception getFrigateUrl: {ex}")

    def loadConfig(self):
        try:
            self.config = {}
            with open("config.yaml", "r") as stream:
                self.config = yaml.safe_load(stream)
        except Exception as ex:
            self.logger.error(f"Config load failed, exception: {ex}")
        
    def main(self):
        try:
            self.loadConfig()
            self.telegram_helper = telegram_helper(self.config, self.logger)

            self.client = mqtt.Client()
            self.client.on_connect = self.onMqttConnect
            self.client.on_message = self.onMqttMessage

            self.client.connect(self.config["mqtt"]["host"], self.config["mqtt"]["port"])

            self.client.loop_forever()
        except Exception as ex:
            self.logger.error(f"Exception main: {ex}")
        
if __name__ == "__main__":
    obj = frigate2telegram()
    obj.main()
