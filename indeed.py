import requests
from bs4 import BeautifulSoup
import csv

class Scraper():                                                    # html데이터 내의 원하는 정보를 걸러내는 매크로
    def __init__(self):
        self.url = "https://kr.indeed.com/jobs?q=python&limit=50"           #url 설정
    def getHTML(self, cnt):                                              #웹사이트 접근 및 html정보 받아는 함수
        res = requests.get(self.url + "&start=" + str(cnt * 50))            #
        if res.status_code != 200:
            print("request error : ", res.status_code)
        html = res.text
        soup = BeautifulSoup(html, "html.parser")
        return soup

    def getPages(self, soup):                                               #전체 페이지 갯수 구하는 함수
        pages = soup.select(".pagination > a")                              #pagination클래스를 갖는 a태그 요소들의 정보
        return len(pages)                                                   #pages내의 마지막 요소의 index+1

    def getCards(self, soup, cnt):                                       #각 페이지 내의 모든 카드 불러오는 함수
        jobCards = soup.find_all("div", class_ = "jobsearch-SerpJobCard")   #job~클래스를 갖는 div태그 중 요소들의 모든 html정보

        jobTitle = []
        jobID = []
        jobLocation = []

        for j in jobCards:
            jobID.append("https://kr.indeed.com/viewjob?jk=" + j["data-jk"])#j["data-jk"] = ?
            jobTitle.append(j.find("a").text.replace("\n",""))
                                                                            # append = ()안에 매개변수를 배열 마지막에 추가
                                                                            # j = jobCards 내의 전체 요소
                                                                            # j.find.text = j에서 ()안에 매개변수를 포함하는 css선택자의 내용 반환||없으면 -1 반환
                                                                            #.text = ?
                                                                            #.replace = 전체 내용 내의 "\n"을 ""로 대체 (=삭제)
            if j.find("div",class_="location") !=None:
                jobLocation.append(j.find("div",class_="location").text)
            elif j.find("span",class_="location") !=None:
                jobLocation.append(j.find("span",class_="location").text)
                                                                            # print(len(jobID), len(jobTitle), len(jobLocation)) = 각 배열 별 값의 갯수가 잃치하는 지 점검
            self.writeCSV(jobID, jobTitle, jobLocation, cnt)

    def writeCSV(self, ID, Title, Location, cnt):                   #csv 파일 생성함수
        file = open("indeed.csv", "a",encoding="UTF-8", newline="")                          #open(파일명[,mode[,buffering]]) = 파일을 열거나 새로 생성
        wr = csv.writer(file)
        for i in range(len(ID)):
            wr.writerow([str(i + 1 + cnt * 50), ID[i], Title[i], Location[i]])
        file.close


    def scrap(self):
        file = open("indeed.csv", "w", encoding="UTF-8", newline="")
        wr = csv.writer(file)
        wr.writerow(["No. ", "Link", "Tiltle", "Location"])
        file.close

        soupPage = self.getHTML(0)
        pages = self.getPages(soupPage)        

        for i in range(pages):
            soupCard = self.getHTML(i)
            self.getCards(soupCard, i)
            print(i +1 , "번쨰 페이지 Done")

if __name__ == "__main__":
    s = Scraper()
    s.scrap()