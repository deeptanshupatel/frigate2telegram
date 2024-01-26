# standard imports
import json
import logging
import urllib.request
from datetime import datetime, timedelta

# third party imports which needs installation
import paho.mqtt.client as mqtt # pip install paho.mqtt
import yaml # pip install pyyaml

# own classes
from telegram_helper import telegram_helper

class frigate2telegram:

    def __init__(self):
        logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename = "/logs/frigate2telegram.log", level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.mqtt_event_history = {}

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
            has_clip = json_data["after"]["has_clip"]
            has_snapshot = json_data["after"]["has_snapshot"]
            before_entered_zones = json_data["before"]["entered_zones"]
            entered_zones = json_data["after"]["entered_zones"]

            log_str = f"camera_name: {camera_name}, event_id: {event_id}, event_type: {event_type}, motion_object: {motion_object}, has_snapshot: {has_snapshot}, has_clip: {has_clip}, entered_zones: {entered_zones}, entered_zones(before): {before_entered_zones}"

            found_details = True
            found_required_zones = self.hasMotionInRequiredZones(camera_name, entered_zones)
            if found_required_zones is False:
                log_str = "Ignored: missing zones, " + log_str
            else:
                found_details = self.hasDetailsToNotify(event_id, event_type, has_snapshot, has_clip)
                if found_details is False:
                    log_str = "Ignored: missing snapshot/clip, " + log_str

            self.logger.info(log_str)

            if found_required_zones is False or found_details is False:
                return

            frigate_url = self.getFrigateUrl(event_type, event_id)
            if frigate_url is not None:
                status, data, data_size = self.readFrigateData(frigate_url)
                if event_type in ["new", "update"]:
                    caption = f"There is a {motion_object} at {camera_name} camera"
                    self.telegram_helper.sendPhoto(status, caption, data, data_size)
                elif event_type == "end":
                    caption = f"Video of {motion_object} at {camera_name} camera"
                    self.telegram_helper.sendVideo(status, caption, data, data_size)
        except Exception as ex:
            self.logger.error(f"Exception onMqttMessage: {ex}")

    def hasDetailsToNotify(self, event_id, event_type, has_snapshot, has_clip):
        can_be_notified = False
        try:
            event_history = self.mqtt_event_history.get(event_id)
            expiry_time = datetime.now() + timedelta(hours=3)
            if event_type in ["new", "update"]:
                if event_history is None:
                    if has_snapshot is True:
                        self.mqtt_event_history[event_id] = {"sent_snapshot": True, "sent_clip": False, "expiry_time": expiry_time}
                        can_be_notified = True
                    else:
                        self.mqtt_event_history[event_id] = {"sent_snapshot": False, "sent_clip": False, "expiry_time": expiry_time}
                else:
                    if event_history["sent_snapshot"] is False and has_snapshot is True:
                        self.mqtt_event_history[event_id]["sent_snapshot"] = True
                        can_be_notified = True
            elif event_type in ["end"]:
                if event_history is None:
                    if has_clip is True:
                        self.mqtt_event_history[event_id] = {"sent_snapshot": True, "sent_clip": True, "expiry_time": expiry_time}
                        can_be_notified = True
                    else:
                        self.mqtt_event_history[event_id] = {"sent_snapshot": True, "sent_clip": False, "expiry_time": expiry_time}
                else:
                    if event_history["sent_clip"] is False and has_clip is True:
                        self.mqtt_event_history[event_id]["sent_clip"] = True
                        can_be_notified = True
                        del self.mqtt_event_history[event_id]
            else:
                self.logger.error(f"Ignored unexpected event_type: {event_type} reported by MQTT server for event_id: {event_id}")
            self.purgeTrackedEventHistory()
        except Exception as ex:
            self.logger.error(f"Exception hasMotionInRequiredZones: {ex}")
        self.logger.info(f"Length of tracked event history: {len(self.mqtt_event_history)}")
        return can_be_notified

    def purgeTrackedEventHistory(self):
        try:
            deleted_keys = ""
            cur_time = datetime.now()
            for key in list(self.mqtt_event_history.keys()):
                expiry_time = self.mqtt_event_history[key].get("expiry_time")
                if expiry_time is not None and expiry_time <= cur_time:
                    deleted_keys += str(key) + ", "
                    del self.mqtt_event_history[key]
            if deleted_keys != "":
                self.logger.info(f"Deleted tracked event history: {deleted_keys}")
        except Exception as ex:
            self.logger.info(f"Exception purgeTrackedEventHistory: {ex}")

    def hasMotionInRequiredZones(self, camera_name, entered_zones):
        try:
            camera_list = self.config["frigate"].get("cameras")
            if camera_list is None:
                return True
            camera_details = camera_list.get(camera_name)
            if camera_details is None:
                return True
            zone_list = camera_details.get("zones")
            if zone_list is None:
                return True
            for each_zone in zone_list:
                if each_zone in entered_zones:
                    return True
        except Exception as ex:
            self.logger.error(f"Exception hasMotionInRequiredZones: {ex}")
        return False

    def getFrigateUrl(self, event_type, event_id):
        try:
            url = None
            if event_type in ["new", "update"]:
                url = f'http://{self.config["frigate"]["host"]}:{self.config["frigate"]["port"]}/api/events/{event_id}/snapshot.jpg?bbox=1&quality=100&timestamp=1'
            elif event_type == "end":
                url = f'http://{self.config["frigate"]["host"]}:{self.config["frigate"]["port"]}/api/events/{event_id}/clip.mp4'
            return url
        except Exception as ex:
            self.logger.error(f"Exception getFrigateUrl: {ex}")

    def readFrigateData(self, url):
        data = ""
        status = 200
        data_size = 0
        try:
            with urllib.request.urlopen(url) as f:
                data = f.read()
                data_size = data.__sizeof__()
        except Exception as ex:
            status = ex.code
            data = ex.read()
            data_size = data.__sizeof__()
            self.logger.error(f"Exception readFrigateData: {ex}")
        data_size = round(data_size/(1024.0**2), 2)
        self.logger.info(f"Snapshot/clip size: {data_size} MB for url: {url}")
        return status, data, data_size

    def loadConfig(self):
        try:
            self.config = {}
            status = True
            with open("/config/config.yaml", "r") as stream:
                self.config = yaml.safe_load(stream)
                if self.config["mqtt"]["host"].startswith("_REPLACE_"):
                    self.logger.error("Invalid MQTT host, no messages will be send out")
                    status = False
                if self.config["frigate"]["host"].startswith("_REPLACE_"):
                    self.logger.error("Invalid Frigate host, no messages will be send out")
                    status = False
                if self.config['telegram']['api_token'].startswith("_REPLACE_") or str(self.config['telegram']['chat_id']).startswith("_REPLACE_"):
                    self.logger.error("Invalid telegram token or chat id, no messages will be send out")
                    status = False
            return status
        except Exception as ex:
            self.logger.error(f"Config load failed, exception: {ex}")
        
    def main(self):
        try:
            if self.loadConfig() == False:
                return

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
