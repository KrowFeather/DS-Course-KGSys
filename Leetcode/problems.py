from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import csv
import re
# 设置Chrome选项
chrome_options = Options()
# chrome_options.add_argument("--headless")  # 无头模式，不打开浏览器窗口
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")

# 设置ChromeDriver路径
service = Service('C:/Users/user/AppData/Local/Google/Chrome/Application/chromedriver.exe')
# 初始化WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# 定义存储数据的列表
name = []
number = []

# 读取同目录下的CSV文件
with open('tag_list.csv', 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    # 遍历每一行数据
    for row in csv_reader:
        # 获取EName和number列的数据
        name.append(row['EName'])
        number.append(row['number'])

for j in range(9,71):
    num = (int)(number[j])+1
    # 目标网址
    url = f"https://leetcode.cn/problem-list/{name[j]}/"

    # 打开目标网页
    driver.get(url)

    # 等待页面加载完成
    time.sleep(5)  # 根据需要调整等待时间


    # 定义滚动函数
    def scroll_to_bottom():
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:  # 增加滚动次数
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # 等待页面加载
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height


    # 滚动页面以加载所有数据
    scroll_to_bottom()

    # 定位到包含要爬取元素的父级div的XPath
    parent_div_xpath = f"/html/body/div[1]/div[1]/div[5]/div/div/div[2]/div[2]/div/div/div[{num}]/div[1]"

    # 创建CSV文件并写入表头
    csv_file = open(f'./list/{name[j]}.csv', 'w', newline='', encoding='utf-8')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['text', 'level', 'tag', 'url'])

    tag = name[j]
    mapping_dict = {
        "简单": 0,
        "中等": 1,
        "困难": 2
    }

    # 遍历子元素
    for i in range(1, num):
        print(i)
        child_div_xpath = f"{parent_div_xpath}/div[{i}]"
        try:
            child_div = driver.find_element(By.XPATH, child_div_xpath)
        except NoSuchElementException:
            print(f"未找到符合xpath表达式 '{child_div_xpath}' 的元素。")
            continue

        try:
            # 获取data-rbd-draggable-id属性值
            draggable_id_value = child_div.get_attribute('data-rbd-draggable-id')
            draggable_id_value = "https://leetcode.cn/problems/" + draggable_id_value + "/description"

            # 查找<div class="ellipsis line-clamp-1">中的内容
            ellipsis_div = child_div.find_element(By.CLASS_NAME, "ellipsis.line-clamp-1")
            ellipsis_text = re.sub(r'\d+\.', '', ellipsis_div.text)

            # 查找<p>中的内容
            p_element = child_div.find_element(By.TAG_NAME, "p")
            p_text = mapping_dict.get(p_element.text, None)
            if p_text is None:
                print(f"输入的 {p_text} 不在映射范围内。")

            # 写入CSV文件
            csv_writer.writerow([ellipsis_text, p_text, tag, draggable_id_value])

        except NoSuchElementException as e:
            print(f"获取元素内容时出错: {e}")

# 关闭CSV文件
csv_file.close()

# 关闭WebDriver
driver.quit()

