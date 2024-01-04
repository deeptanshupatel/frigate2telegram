import telegram
import asyncio
import urllib.request

class telegram_helper:

    def init(self, config, logger):
        self.config = config
        self.logger = logger    
        self.bot = telegram.Bot(token = self.config['telegram']['api_token'])

    def sendPhoto(self, photo_url):
        try:
            photo_data = urllib.request.urlopen(photo_url)
            res = asyncio.run(self.bot.send_photo(chat_id = self.config['telegram']['chat_id'], photo = photo_data))
        except Exception as ex:
            self.logger.error(f"Exception sendPhoto: {ex}")

    def sendVideo(self, video_url):
        try:
            video_data = urllib.request.urlopen(video_url)
            res = asyncio.run(self.bot.send_video(chat_id = self.config['telegram']['chat_id'], video = video_data))
        except Exception as ex:
            self.logger.error(f"Exception sendVideo: {ex}")