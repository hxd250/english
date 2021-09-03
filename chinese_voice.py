"""
    将中文转为语音
    基于百度api
"""

from aip import AipSpeech
from playsound import playsound
from os import remove


class Voice:
    def __init__(self, root_path):
        self.path = root_path
        self.music_name = "music_zh.mp3"
        self.flag = True
        self.APP_ID = '24126167'
        self.API_KEY = '25HTbPCwWqMCtEGC50zWvhts'
        self.SECRET_KEY = '9ObA4EnexficoaEv2n4B83Nh0LuCco4o'
        self.client = AipSpeech(self.APP_ID, self.API_KEY, self.SECRET_KEY)

    def download(self, text, vol, spd, pid, per):
        """
        默认保存的是  music.mp3
        :param text:
        :return:
        """
        result = self.client.synthesis(text, 'zh', 1, {
            'vol': vol, 'spd': spd, 'pid': pid, 'per': per
        })
        if not isinstance(result, dict):
            # print("成功")
            if self.flag:
                try:
                    remove(self.path+self.music_name)
                except:
                    pass
            with open(self.path+self.music_name, 'wb') as f:
                f.write(result)
        else:
            print("下载语音发送错误！")

    def play(self):
        playsound(self.path+self.music_name)


if __name__ == '__main__':
    voice = Voice("./source/")
    voice.download(text="养育，抚养；培养", vol=1, spd=9, pid=0, per=3)
    # 音量(0-15) ，速度(0-9)， 音调(0-9)， 发音人(0,1,3,4)
    voice.play()
