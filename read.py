""""
    读取csv文件的单词或或中文
"""
import csv
from os import rename, remove


class Read:
    def __init__(self, file_name):
        self.completed_path = "./source/completed/"
        self.surplus_path = "./source/surplus/"
        self.file_name = file_name
        pass

    def read_line(self, line_num):
        """
        读取指定数量的单词
        :param line_num: 单词个数
        :return: 返回具体单词或 异常数
        """
        data = []
        f = open(self.surplus_path + self.file_name, "r", encoding="utf8")
        fq_iterator = csv.reader(f)
        while line_num:
            data.append(next(fq_iterator))
            line_num -= 1
        f.close()
        # self.preservation_surplus(data)
        # self.preservation_completed(data)
        return data

    def preservation_completed(self, data):
        """
        更新完成单词文件
        :param data: 听写的单词
        :return:
        """
        with open(self.completed_path+self.file_name, "a+", encoding="utf8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(data)

    def preservation_surplus(self, data):
        """
        更新剩余单词文件
        :param data: csv的迭代器
        :return:
        """
        with open(self.surplus_path+"tmp.csv", "w", encoding="utf8", newline="") as f:
            writer = csv.writer(f)
            with open(self.surplus_path + self.file_name, "r", encoding="utf8") as fq:
                reader = csv.reader(fq)
                for line in reader:
                    if line not in data:
                        writer.writerow(line)
        fq.close()
        remove(self.surplus_path+self.file_name)
        rename(self.surplus_path+"tmp.csv", self.surplus_path+self.file_name)


if __name__ == '__main__':
    read = Read("six.csv")
    print(read.read_line(10))