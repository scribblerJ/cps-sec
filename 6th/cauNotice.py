from selenium import webdriver
from bs4 import BeautifulSoup
import os
import time

path = os.getcwd() + "/chromedriver.exe"

driver = webdriver.Chrome(path)

try:
    driver.get("https://www.cau.ac.kr/cms/FR_CON/index.do?MENU_ID=100#page1")
    time.sleep(1)

    html = driver.page_source # request.get().text와 같은 의미?
    bs = BeautifulSoup(html, "html.parser")

    pages = bs.find("div", class_ = "pagination").find_all("a")[-1]["href"].split("page")[1] #find_all => list로 결과를 return
    pages = int(pages)

    title = []
    for i in range(3):
        driver.get("https://www.cau.ac.kr/cms/FR_CON/index.do?MENU_ID=100#page1" + str(i + 1))
        time.sleep(3)

        html = driver.page_source
        bs = BeautifulSoup(html, "html.parser")

        cont = bs.find_all("div", class_ = "txtL")
        title.append("page" + str(i + 1))
        for c in consts :
            title.append(c.find("a").text)
            
finally:
    # time.sleep(3)
    for t in title:
        if t.find("page") != -1:
            print()
            print(t)
        else:
            print(t) 
    driver.quit()
