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

# 目标网址
url = "https://leetcode.cn/problemset/"

# 打开目标网页
driver.get(url)

# 等待页面加载完成
time.sleep(5)  # 根据需要调整等待时间


# 定位到包含要爬取元素的父级div的XPath
parent_div_xpath = "/html/body/div[1]/div[1]/div[5]/div[2]/div[1]/div[3]/div[1]/div[1]"

# 创建CSV文件并写入表头
csv_file = open('tag_list.csv', 'w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['EName', 'CName','number',])



# 遍历子元素
for i in range(1, 72):
    print(i)
    child_div_xpath = f"{parent_div_xpath}/div[{i}]"

    try:
        child_div = driver.find_element(By.XPATH, child_div_xpath)
    except NoSuchElementException:
        print(f"未找到符合xpath表达式 '{child_div_xpath}' 的元素。")
        continue

    try:
        # 查找<a class="inline-flex items-center">中的内容
        a_element = child_div.find_element(By.XPATH, ".//a[@class='inline-flex items-center']")
        tag_name = a_element.get_attribute('href').split('/')[-1]

        # 查找<a>下的两个<span>元素
        span_elements = a_element.find_elements(By.TAG_NAME, "span")
        span1_text = span_elements[0].text if len(span_elements) > 0 else ""
        span2_text = span_elements[1].text if len(span_elements) > 1 else ""

        # 写入CSV文件
        csv_writer.writerow([tag_name, span1_text,span2_text])

    except NoSuchElementException as e:
        print(f"获取元素内容时出错: {e}")

# 关闭CSV文件
csv_file.close()

# 关闭WebDriver
driver.quit()

