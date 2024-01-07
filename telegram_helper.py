import requests

class telegram_helper:

    def __init__(self, config, logger):
        try:
            self.config = config
            self.logger = logger    
            self.bot_token = self.config['telegram']['api_token']
            self.bot_chat_id = self.config['telegram']['chat_id']
            self.base_url = "https://api.telegram.org/bot" + self.bot_token
        except Exception as ex:
            self.logger.error(f"Exception __init__: {ex}")

    def sendMessage(self, message_data):
        try:
            # telegram API: https://core.telegram.org/bots/api#sendmessage
            telegram_message_url = self.base_url + "/sendMessage"
            if message_data != "":
                data = {"chat_id": self.bot_chat_id, 'text': message_data, "timeout": 30}
                resp = requests.post(telegram_message_url, data=data)
                if resp.status_code != 200:
                    self.logger.error(f"sendMessage error: failed to send message, status: {resp.status_code}, reason: {resp.reason}, text: {resp.text}")
        except Exception as ex:
            self.logger.error(f"Exception sendMessage: {ex}")

    def sendPhoto(self, status, caption, photo_data):
        try:
            # telegram API: https://core.telegram.org/bots/api#sendphoto
            telegram_photo_url = self.base_url + "/sendPhoto"
            if status == 200 and photo_data != "":
                files = {'photo': photo_data}
                data = {"chat_id": self.bot_chat_id, "caption": caption, "timeout": 30}
                resp = requests.post(telegram_photo_url, data=data, files=files)
                if resp.status_code != 200:
                    msg = f"sendPhoto error: failed to send photo, status: {resp.status_code}, reason: {resp.reason}, text: {resp.text}"
                    self.logger.error(msg)
                    self.sendMessage(msg)
        except Exception as ex:
            self.logger.error(f"Exception sendPhoto: {ex}")

    def sendVideo(self, status, caption, video_data):
        try:
            # telegram API: https://core.telegram.org/bots/api#sendvideo
            telegram_video_url = self.base_url + "/sendVideo"
            if status == 200 and video_data != "":
                files = {'video': video_data}
                data = {"chat_id": self.bot_chat_id, "caption": caption, "timeout": 30}
                resp = requests.post(telegram_video_url, data=data, files=files)
                if resp.status_code != 200:
                    msg = f"sendVideo error: failed to send video, status: {resp.status_code}, reason: {resp.reason}, text: {resp.text}"
                    self.logger.error(msg)
                    self.sendMessage(msg)
        except Exception as ex:
            self.logger.error(f"Exception sendVideo: {ex}")

    
