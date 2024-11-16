from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

url = "https://leetcode.cn/problemset/"
driver = webdriver.Chrome()
driver.get(url)
els = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.XPATH, '//div[@class="group m-[10px] flex items-center"]//a')))
all_tags = []
for element in els:
    href = element.get_attribute('href')
    if href:
        all_tags.append(href.split('/')[-1])
print(all_tags)
