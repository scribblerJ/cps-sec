import requests
from bs4 import BeautifulSoup

req = requests.get("https//movie.naver.com/movie/running/current.nhn")
html = req.text
bs = BeautifulSoup(html, "htmnl.parser")

listDetail = bs.select(".lst_detail_t1")
# print(listDetail)

for i in listDetail :
    li = i.find_all("li")
    for l in li:
        de = l.find("dt", class_= "tit")
        title = dt.find("a").text
        print(title)