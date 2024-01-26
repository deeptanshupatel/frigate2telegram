import requests

class telegram_helper:

    def __init__(self, config, logger):
        try:
            self.config = config
            self.logger = logger
            self.bot_token = self.config['telegram']['api_token']
            self.bot_chat_id = self.config['telegram']['chat_id']
            self.max_snapshot_size_mb = int(self.config['telegram']['max_snapshot_size_mb'])
            self.max_clip_size_mb = int(self.config['telegram']['max_clip_size_mb'])
            self.base_url = "https://api.telegram.org/bot" + self.bot_token
            self.sendMessage("frigate2telegram got started!")
        except Exception as ex:
            self.logger.error(f"Exception __init__: {ex}")

    def sendMessage(self, message_data):
        try:
            # telegram API: https://core.telegram.org/bots/api#sendmessage
            telegram_message_url = self.base_url + "/sendMessage"
            if message_data != "":
                data = {"chat_id": self.bot_chat_id, 'text': message_data}
                resp = requests.post(telegram_message_url, data=data, timeout=30)
                if resp.status_code == 200:
                    self.logger.info("Sent message successfully")
                else:
                    self.logger.error(f"sendMessage error: failed to send, status: {resp.status_code}, reason: {resp.reason}, text: {resp.text}")
        except Exception as ex:
            self.logger.error(f"Exception sendMessage: {ex}")

    def sendPhoto(self, status, caption, photo_data, data_size):
        try:
            if data_size > self.max_snapshot_size_mb:
                msg = f"Snapshot is too large {data_size} MB and can't be send for '{caption}'"
                self.sendMessage(msg)
                self.logger.error(msg)
                return

            # telegram API: https://core.telegram.org/bots/api#sendphoto
            telegram_photo_url = self.base_url + "/sendPhoto"
            if status == 200 and photo_data != "":
                files = {'photo': photo_data}
                data = {"chat_id": self.bot_chat_id, "caption": caption}
                resp = requests.post(telegram_photo_url, data=data, files=files, timeout=30)
                if resp.status_code == 200:
                    self.logger.info("Sent snapshot successfully")
                else:
                    msg = f"sendPhoto error: failed to send, status: {resp.status_code}, reason: {resp.reason}"
                    self.logger.error(f"{msg}, text: {resp.text}")
                    self.sendMessage(msg)
        except Exception as ex:
            self.logger.error(f"Exception sendPhoto: {ex}")

    def sendVideo(self, status, caption, video_data, data_size):
        try:
            if data_size > self.max_clip_size_mb:
                msg = f"Video is too large {data_size} MB and can't be send for '{caption}'"
                self.sendMessage(msg)
                self.logger.error(msg)
                return

            # telegram API: https://core.telegram.org/bots/api#sendvideo
            telegram_video_url = self.base_url + "/sendVideo"
            if status == 200 and video_data != "":
                files = {'video': video_data}
                data = {"chat_id": self.bot_chat_id, "caption": caption}
                resp = requests.post(telegram_video_url, data=data, files=files, timeout=30)
                if resp.status_code == 200:
                    self.logger.info("Sent clip successfully")
                else:
                    msg = f"sendVideo error: failed to send, status: {resp.status_code}, reason: {resp.reason}"
                    self.logger.error(f"{msg}, text: {resp.text}")
                    self.sendMessage(msg)
        except Exception as ex:
            self.logger.error(f"Exception sendVideo: {ex}")
