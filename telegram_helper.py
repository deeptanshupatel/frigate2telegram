import telegram
import asyncio
import urllib.request
import requests

class telegram_helper:

    def __init__(self, config, logger):
        try:
            self.config = config
            self.logger = logger    
            self.bot = telegram.Bot(token = self.config['telegram']['api_token'])
        except Exception as ex:
            self.logger.error(f"Exception __init__: {ex}")

    def sendPhoto(self, photo_url):
        try:
            with urllib.request.urlopen(photo_url) as photo_data:
                asyncio.run(self.bot.send_photo(chat_id = self.config['telegram']['chat_id'], photo = photo_data))
        except Exception as ex:
            self.logger.error(f"Exception sendPhoto: {ex}")

    def sendVideo(self, video_url):
        try:
            #with urllib.request.urlopen(video_url) as video_data:
                #asyncio.run(self.bot.send_video(chat_id = self.config['telegram']['chat_id'], video = video_data, write_timeout = 30, pool_timeout = 30))
            self.sendVideoDirect(video_url)
        except Exception as ex:
            self.logger.error(f"Exception sendVideo: {ex}")

    def sendVideoDirect(self, video_url):
        try:
            # telegram API: https://core.telegram.org/bots/api#sendvideo
            bot_token = self.config['telegram']['api_token']
            bot_chat_id = self.config['telegram']['chat_id']
            url = "https://api.telegram.org/bot" + bot_token + "/sendVideo"
            status, file_url_data = self.read_url_data(video_url)
            if status == 200 and file_url_data != "":
                files = {'video': file_url_data}
                data = {"chat_id": bot_chat_id, "timeout": 30}
                r = requests.post(url, data=data, files=files)
                if r.status_code != 200:
                    self.logger.error(f"sendVideoDirect error: failed to send video, status: {r.status_code}, reason: {r.reason}, text: {r.text}")
            else:
                self.logger.error(f"sendVideoDirect error: failed to load data from {video_url}, error: {file_url_data}")
        except Exception as ex:
            self.logger.error(f"Exception sendVideoDirect: {ex}")

    def read_url_data(self, url):
        data = ""
        status = 200
        try:
            with urllib.request.urlopen(url) as f:
                data = f.read()
        except Exception as e:
            status = e.code
            data = e.read()
        return status, data

