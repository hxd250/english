from PySide2.QtWidgets import QApplication, QMessageBox, QDialog, QTextBrowser
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QIcon
from PySide2.QtCore import Signal, QObject
from random import choice
from time import sleep
from threading import Thread
from re import findall
from PySide2.QtWidgets import QFileDialog
import csv
import json
from os.path import split
from requests import get

# 自定义模块
from read import Read
from chinese_voice import Voice as ChVoice
from english_voice import Voice as EnVoice


class MySignals(QObject):
    # 定义一种信号，两个参数 类型分别是： QTextBrowser 和 字符串
    # 调用 emit方法 发信号时，传入参数 必须是这里指定的 参数类型
    text_print = Signal(QTextBrowser, str)

    # 还可以定义其他种类的信号
    update_table = Signal(str)


def get_default():
    with open("./source/default.json", "r", encoding="utf8") as f:
        return json.load(f)


def modify_text(fb, text):
    fb.appendPlainText(text)
    fb.ensureCursorVisible()


class MyForm(QDialog):
    def __init__(self):
        super().__init__()
        self.default = get_default()
        self.read = Read(self.default['default_file'])
        self.envoice = EnVoice("./source/music/")
        self.chvoice = ChVoice("./source/music/")
        self.ui = QUiLoader().load('./source/main.ui')  # 加载ui文件
        self.word_num = self.default["default_word_num"]
        self.word_max = 15
        self.texts = ""
        self.flag = False
        self.ui.fileedit.setReadOnly(True)
        self.ui.fileedit2.setReadOnly(True)
        # 加载默认设置到设置界面
        self.ui.fileedit.setText(self.default["default_file"])
        self.ui.defaultnumBox.setValue(self.default["default_word_num"])
        self.ui.defaultrepeatbox.setValue(self.default["default_repeat_num"])
        self.ui.defaultvoiceintervalbox.setValue(self.default["default_voice_interval"])
        self.ui.defaultwordintervalbox.setValue(self.default["default_word_interval"])
        self.ui.speadbox.setValue(self.default["default_speed"])
        self.ui.defaultenbutton.setChecked(self.default["en"][0])
        self.ui.defaultusabutton.setChecked(self.default["en"][1])
        self.ui.defaultfemalebutton.setChecked(self.default["ch"][0])
        self.ui.defaultmalebutton.setChecked(self.default["ch"][1])
        self.ui.defaultdubutton.setChecked(self.default["ch"][2])
        self.ui.defaultduyayabutton.setChecked(self.default["ch"][3])
        # 加载默认设置到听写界面
        self.ui.numbox.setValue(self.default['default_word_num'])
        self.ui.timebox.setValue(self.default['default_word_interval'])
        self.voice_interval = self.default["default_voice_interval"]
        self.ui.repeatnumbox.setValue(self.default['default_repeat_num'])
        self.ui.enbutton.setChecked(self.default['en'][0])
        self.ui.usabutton.setChecked(self.default['en'][1])
        self.ui.radioButton.setChecked(self.default['ch'][0])
        self.ui.radioButton_2.setChecked(self.default['ch'][1])
        self.ui.radioButton_3.setChecked(self.default['ch'][2])
        self.ui.radioButton_4.setChecked(self.default['ch'][3])

        self.ui.text.setReadOnly(True)
        # self.ui.usabutton.setChecked(False)
        # self.setMouseTracking(True)

        # 监听
        self.ui.showbutton.clicked.connect(self.show_word)
        self.ui.inputbutton.clicked.connect(self.import_word)
        self.ui.filebutton.clicked.connect(self.choice_file)
        self.ui.showhistorybutton.clicked.connect(self.choice_file2)
        self.ui.savebutton.clicked.connect(self.save_default)
        self.ui.startbutton.clicked.connect(self.task)
        self.ui.readaloudbutton.clicked.connect(self.read_aloud)
        self.ui.writebutton.clicked.connect(self.write_words)
        # 信号量
        self.ms = MySignals()
        self.ms.text_print.connect(modify_text)

    # 写入的单词表
    def write_words(self):
        if self.ui.writebutton.text() == "手动导入":
            self.ui.writebutton.setText("确定")
            self.ui.startbutton.setEnabled(False)
            self.ui.showbutton.setEnabled(False)
            self.ui.inputbutton.setEnabled(False)
            self.ui.readaloudbutton.setEnabled(False)
            self.ui.text.setReadOnly(False)
            return
        data = []
        texts = self.ui.text.toPlainText()
        lines = texts.strip().split("\n")
        for line in lines:
            # print(line.split())
            if line and 2 == len(line.split()):
                data.append(line.split())
                self.ui.startbutton.setEnabled(True)
                self.ui.showbutton.setEnabled(True)
                self.ui.inputbutton.setEnabled(True)
                self.ui.readaloudbutton.setEnabled(True)
            elif 0 == len(line.split()):
                self.ui.startbutton.setEnabled(True)
                self.ui.showbutton.setEnabled(True)
                self.ui.inputbutton.setEnabled(True)
                self.ui.readaloudbutton.setEnabled(True)
            else:
                QMessageBox.warning(
                    self.ui,
                    "警告",
                    "请输入如下格式: \nword1\tmean1\nword2\tmean2\nword3\tmean3\n..."
                )
                return
        # print(data)
        self.texts = data
        self.word_num = len(data)
        if self.word_num:
            self.ui.numbox.setValue(self.word_num)
        # 导入后输入框设置为只读
        self.ui.writebutton.setText("手动导入")
        self.ui.text.setReadOnly(True)
        self.flag = True

    # 保存默认值
    def save_default(self):
        self.default = {
            "default_file": self.ui.fileedit.text(),
            "default_word_num": self.ui.defaultnumBox.value(),
            "default_repeat_num": self.ui.defaultrepeatbox.value(),
            "default_word_interval": self.ui.defaultwordintervalbox.value(),
            "default_voice_interval": self.ui.defaultvoiceintervalbox.value(),
            "default_speed": self.ui.speadbox.value(),
            "en": [
                self.ui.defaultenbutton.isChecked(),
                self.ui.defaultusabutton.isChecked()],
            "ch": [
                self.ui.defaultfemalebutton.isChecked(),
                self.ui.defaultmalebutton.isChecked(),
                self.ui.defaultdubutton.isChecked(),
                self.ui.defaultduyayabutton.isChecked()],
        }
        # print(self.default)
        # 更新听写界面的选项
        self.read = Read(self.default["default_file"])
        self.ui.numbox.setValue(self.default['default_word_num'])
        self.ui.timebox.setValue(self.default['default_word_interval'])
        self.voice_interval = self.default["default_voice_interval"]
        self.ui.repeatnumbox.setValue(self.default['default_repeat_num'])
        self.ui.enbutton.setChecked(self.default['en'][0])
        self.ui.usabutton.setChecked(self.default['en'][1])
        self.ui.radioButton.setChecked(self.default['ch'][0])
        self.ui.radioButton_2.setChecked(self.default['ch'][1])
        self.ui.radioButton_3.setChecked(self.default['ch'][2])
        self.ui.radioButton_4.setChecked(self.default['ch'][3])
        with open("./source/default.json", "w", encoding="utf8") as f:
            f.write(json.dumps(self.default, ensure_ascii=False))
        QMessageBox.information(
            self.ui,
            '提示',
            '保存成功！'
        )

    # 展示历史听写的单词
    def show_history(self):
        num = 0
        self.ui.text2.clear()
        file_path = self.ui.fileedit2.text()
        # print(file_path)
        if not file_path:
            # QMessageBox.critical(
            #     self.ui,
            #     '错误',
            #     '请输入文件路径！')
            return
        try:
            with open(file_path, "r", encoding="utf8") as f:
                reader = csv.reader(f)
                for line in reader:
                    self.ui.text2.append(f"{(self.word_max - len(line[0])) * ' '}".join(line))
                    num += 1
            self.ui.numbutton.setText(str(num))
        except Exception as e:
            # print(e)
            QMessageBox.critical(
                self.ui,
                '错误',
                '文件不存在！')

    # 历史记录的选择文件
    def choice_file2(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self.ui,  # 父窗口对象
            "选择你要查看的表格文件",  # 标题
            r"./source/completed",  # 起始目录
            "图片类型 (*.csv)"  # 选择类型过滤项，过滤内容在括号中
        )
        self.ui.fileedit2.setText(filepath)
        self.show_history()

    # 设置位置的选择文件
    def choice_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self.ui,  # 父窗口对象
            "选择听写表格",  # 标题
            r"./source/dictionary",  # 起始目录
            "图片类型 (*.csv)"  # 选择类型过滤项，过滤内容在括号中
        )
        self.ui.fileedit.setText(split(filepath)[1])

    # 获取发音type
    def get_type(self):
        if self.ui.usabutton.isChecked():
            return 2
        elif self.ui.enbutton.isChecked():
            return 1

    # 获取中文发音类型
    def get_per(self):
        if self.ui.radioButton.isChecked():
            return 0
        if self.ui.radioButton_2.isChecked():
            return 1
        if self.ui.radioButton_3.isChecked():
            return 3
        else:
            return 4

    # 显示单词
    def show_word(self):
        self.ui.text.clear()
        for text in self.texts:
            # print(text)
            self.ui.text.appendPlainText(f"{(self.word_max - len(text[0])) * ' '}".join(text))

    # 导入单词
    def import_word(self):
        if not self.default["default_file"]:
            QMessageBox.warning(
                self.ui,
                "警告",
                "请先在设置界面选择单词表！"
            )
            return
        self.flag = True
        self.ui.text.clear()
        self.word_num = self.ui.numbox.value()
        self.texts = self.read.read_line(self.word_num)
        for text in self.texts:
            # print(text)
            self.ui.text.appendPlainText(f"{(self.word_max - len(text[0])) * ' '}".join(text))


    # 朗读英语
    def read_aloud(self):
        # 检查网络
        try:
            get("http://www.baidu.com")
        except:
            QMessageBox.warning(
                self.ui,
                "警告",
                "网络在开小差! ^_^"
            )
            return

        if not self.texts:
            QMessageBox.warning(
                self.ui,
                '提示',
                '没有单词可读哟！')
            return
        word_interval = self.ui.timebox.value()
        repeat = int(self.ui.repeatnumbox.value())
        type_ = self.get_type()
        self.ui.startbutton.setEnabled(False)
        self.ui.showbutton.setEnabled(False)
        self.ui.inputbutton.setEnabled(False)
        self.ui.readaloudbutton.setEnabled(False)
        self.ui.writebutton.setEnabled(False)

        def func():
            for i in range(self.word_num):
                word = self.texts[i][0]
                self.envoice.download(word, type_)
                for _ in range(repeat):
                    self.envoice.play()
                    sleep(self.voice_interval)
                sleep(word_interval)
            self.ui.startbutton.setEnabled(True)
            self.ui.showbutton.setEnabled(True)
            self.ui.inputbutton.setEnabled(True)
            self.ui.readaloudbutton.setEnabled(True)
            self.ui.writebutton.setEnabled(True)
        t = Thread(target=func)
        t.setDaemon(True)
        t.start()

    # 听写主函数
    def task(self):
        # 检查网络
        try:
            get("http://www.baidu.com")
        except:
            QMessageBox.warning(
                self.ui,
                "警告",
                "网络在开小差! ^_^"
            )
            return
        if not self.texts:
            QMessageBox.warning(
                self.ui,
                '警告',
                '请先导入单词！')
            return
        self.ui.startbutton.setEnabled(False)
        self.ui.showbutton.setEnabled(False)
        self.ui.inputbutton.setEnabled(False)
        self.ui.readaloudbutton.setEnabled(False)
        self.ui.writebutton.setEnabled(False)

        # 获取间隔时间
        word_interval = self.ui.timebox.value()
        # 获取发音次数
        repeat = int(self.ui.repeatnumbox.value())
        # 获取发音type
        type_ = self.get_type()
        per = self.get_per()

        self.ui.text.clear()
        index_list = list(range(self.word_num))
        # print(self.texts)

        def my_thread():
            for i in range(self.word_num):
                # 打乱听写
                index = choice(index_list)
                index_list.remove(index)

                word = self.texts[index][0]
                mean = self.texts[index][1]
                flag = choice([0, 1])
                # 英文语音
                if flag != 0:
                    self.ms.text_print.emit(self.ui.text, f"正在听写第{i + 1}个单词...")
                    self.envoice.download(word, type_)
                    for _ in range(repeat):
                        self.envoice.play()
                        sleep(self.voice_interval)
                # 中文语音
                else:
                    self.ms.text_print.emit(self.ui.text, f"正在听写第{i + 1}个单词...{mean}")
                    # 去除词性符号
                    dis_list = findall("[a-z]+", mean)
                    text = mean
                    for dis in dis_list:
                        text = text.replace(dis, "")
                    # print(text)
                    self.chvoice.download(text=text, vol=5, spd=self.default["default_speed"], pid=1, per=per)
                    for _ in range(repeat):
                        self.chvoice.play()
                        sleep(self.voice_interval)
                sleep(word_interval)
            self.ms.text_print.emit(self.ui.text, "-"*10+"\n听写完毕\n")
            self.ui.startbutton.setEnabled(True)
            self.ui.showbutton.setEnabled(True)
            self.ui.inputbutton.setEnabled(True)
            self.ui.readaloudbutton.setEnabled(True)
            self.ui.writebutton.setEnabled(True)
            # 听写完毕后，更新文件
            if self.flag:
                try:
                    self.read.preservation_surplus(self.texts)
                    self.read.preservation_completed(self.texts)
                except:
                    QMessageBox.critical(
                        self.ui,
                        '错误',
                        '本次听写文件保存错误！')
                self.flag = False

        t = Thread(target=my_thread)
        t.setDaemon(True)
        t.start()


if __name__ == '__main__':
    app = QApplication([])
    app.setWindowIcon(QIcon("./source/icon.ico"))
    stats = MyForm()
    stats.ui.show()
    app.exec_()
