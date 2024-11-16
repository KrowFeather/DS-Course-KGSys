from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def crawlAllConcepts():
    all_concepts = []
    driver = webdriver.Chrome()
    driver.get("https://oiwiki.org/")
    els = WebDriverWait(driver, 100).until(EC.presence_of_all_elements_located((By.XPATH, "//span[contains(@class, 'md-ellipsis')]")))
    print(els)
    for element in els:
        text = driver.execute_script("return arguments[0].innerText;", element)
        print(text)
        if text:
            all_concepts.append(text)

    return all_concepts

concepts = crawlAllConcepts()
print(concepts)