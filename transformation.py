import csv
import re
import xlrd


# ./source/six.txt -->  *.csv
def txt2csv(oldfile, newfile):
    word = ""
    mean = ""
    fq = open(newfile, "w", newline="", encoding="utf8")
    writer = csv.writer(fq)
    with open(oldfile, "r", encoding="utf8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line:
                # print(line)
                x = line.split(" ")
                # print(x)
                for i in x:
                    # 判断是否是单词，即纯字母
                    if i.isalpha():
                        if mean != "":
                            writer.writerow([word.replace(" ", ""), mean.strip().replace(" ", "")])
                            print([word.replace(" ", ""), mean.replace(" ", "")])
                            word = ""
                            mean = ""
                        word = i
                        # print(i)
                    elif i != "":
                        mean = mean + "  " + i
                        # print(i)
            # break
    fq.close()


# 六级词汇600.xls --> *.csv
def xls2csv(oldfile, newfile):
    f = open(newfile, "w", encoding="utf8", newline="")
    writer = csv.writer(f)
    book = xlrd.open_workbook(oldfile)
    if not book.sheet_loaded(sheet_name_or_index=0):
        print("导入错误")
        return
    sheet1 = book.sheet_by_index(0)
    for i in range(sheet1.nrows):
        data = sheet1.row_values(i)
        texts = [data[0], data[1][2::].replace(" ", "")+"\t"+data[2][2::].replace(" ", "")]
        print(texts)
        writer.writerow(texts)
    f.close()

# 


if __name__ == '__main__':
    txt2csv("./source/six.txt", "./source/dictionary/六级词汇2000.csv")
    # xls2csv("./source/六级词汇600.xls", "./source/dictionary/六级词汇600.csv")