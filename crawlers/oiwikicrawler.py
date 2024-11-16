from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def crawlAllConcepts():
    all_concepts = []
    driver = webdriver.Chrome()
    driver.get("https://oiwiki.org/")

    # 等待页面加载，找到所有包含概念的元素
    els = WebDriverWait(driver, 100).until(
        EC.presence_of_all_elements_located((By.XPATH, "//span[contains(@class, 'md-ellipsis')]")))

    for element in els:
        text = driver.execute_script("return arguments[0].innerText;", element)
        if text:
            all_concepts.append(text)

    driver.quit()
    return all_concepts


def saveConceptsToFile(concepts, file_path):
    with open(file_path, 'a', encoding='utf-8') as f:
        for concept in concepts:
            f.write(concept + '\n')  # 每个概念写入一行，并添加换行符


# 调用函数获取概念列表并保存
concepts = crawlAllConcepts()
print(concepts)

saveConceptsToFile(concepts, './concepts.txt')
