"""
    将英文转为语音
    基于有道爬虫
"""

import requests
from playsound import playsound
from os import remove


class Voice:
    def __init__(self, path):
        self.base_url = "https://dict.youdao.com/dictvoice?audio={}&type={}"
        self.path = path
        self.music_name = "music_en.mp3"
        self.flag = True
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51"
        }

    def download(self, word, type_):
        response = requests.get(url=self.base_url.format(word, type_), headers=self.headers).content
        if self.flag:
            try:
                remove(self.path+self.music_name)
            except:
                pass
        with open(self.path+self.music_name, "wb") as f:
            f.write(response)

    def play(self):
        playsound(self.path+self.music_name)


if __name__ == '__main__':
    voice = Voice("./source/")
    voice.download("newspaper", 0)
    voice.play()



