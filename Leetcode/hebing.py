import os
import csv

# 定义存储数据的字典
data_dict = {}

# 遍历./list目录下的所有csv文件
for filename in os.listdir('./list'):
    if filename.endswith('.csv'):
        with open(os.path.join('./list', filename), 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            # 遍历每一行数据
            for row in csv_reader:
                text = row['text']
                level = row['level']
                tag = row['tag']
                url = row['url']

                # 如果text列数据已经存在，则将tag中的数据加在已经存在的数据的tag中
                if text in data_dict:
                    data_dict[text]['tag'] += f", {tag}"
                else:
                    data_dict[text] = {'level': level, 'tag': tag, 'url': url}

# 将数据写入all.csv文件
with open('all.csv', 'w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['text', 'level', 'tag', 'url']
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    # 写入表头
    csv_writer.writeheader()

    # 写入数据
    for text, data in data_dict.items():
        csv_writer.writerow({'text': text, 'level': data['level'], 'tag': data['tag'], 'url': data['url']})

# 打印结果
print("数据已合并到all.csv文件中。")