# third party imports which needs installation
import paho.mqtt.client as mqtt # pip install paho.mqtt
import yaml # pip install pyyaml

# standard imports
import json
import logging

# own classes
from telegram_helper import telegram_helper

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename = "frigate2telegram.log", level=logging.INFO)
logger = logging.getLogger(__name__)

class frigate2telegram:

    def on_connect(self, client, userdata, flags, rc):
        logger.info("Connected to mqtt server result code: " + str(rc))    
        client.subscribe("frigate/events")

    def on_message(self, client, userdata, msg):
        json_data = json.loads(msg.payload)
        logger.info(f"cam: {json_data['after']['camera']}, type: {json_data['type']}, label: {json_data['after']['label']}")
        camera_name = json_data['after']['camera']
        self.telegram_helper.sendPhoto(photo_url = self.getPhotoUrl(camera_name))

    def getPhotoUrl(self, camera_name):
        photo_url = f'http://{self.config["frigate"]["host"]}:{self.config["frigate"]["port"]}/api/{camera_name}/latest.jpg?bbox=1&quality=100'
        return photo_url
    
    def getVideoUrl(self, camera_name):
        video_url = f'http://{self.config["frigate"]["host"]}:{self.config["frigate"]["port"]}/api/{camera_name}/latest.jpg?bbox=1&quality=100'
        return video_url

    def loadConfig(self):
        config = {}
        with open("config.yaml", "r") as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logger.error(exc)
        return config
    
    def main(self):
        self.config = self.loadConfig()
        self.telegram_helper = telegram_helper()
        self.telegram_helper.init(self.config, logger)

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(self.config["mqtt"]["host"], self.config["mqtt"]["port"])

        self.client.loop_forever()

if __name__ == "__main__":
    obj = frigate2telegram()
    obj.main()
