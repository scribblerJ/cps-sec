import requests
from bs4 import BeautifulSoup
import csv

class Scraper():                                                    # html데이터 내의 원하는 정보를 걸러내는 매크로
    def __init__(self):
        self.url = "https://kr.indeed.com/jobs?q=python&limit=50"           #url 설정
    def getHTML(self, cnt):                                              #웹사이트 접근 및 html정보 받아는 함수
        res = requests.get(self.url + "&start=" + str(cnt * 50))            #해당 url주소에 html 파일 요청
        if res.status_code != 200:                                          #파일이 없거나 기타 오류가 있는 경우
            print("request error : ", res.status_code)
        html = res.text                                                     #.text = str객체를 반환
        soup = BeautifulSoup(html, "html.parser")                           #BeautifulSoup(변환하려는 문자열, 사용하는 라이브러리 = 도구)
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
            jobID.append("http://kr.indeed.com/viewjob?jk=" + j["data-jk"])#j["data-jk"] = ?
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
        self.writeCSV(jobID, jobTitle, jobLocation, cnt)                    #정리된 모든 정보 writeCSV함수로 파일에 추가

    def writeCSV(self, ID, Title, Location, cnt):                   #csv파일 수정함수
        file = open("indeed.csv", "a",encoding="UTF-8", newline="")          #open(파일명, a, endcoding, newline) => a = 파일 마지막에 새로운 내용 추가, encoding, newline = ?
        wr = csv.writer(file)
        for i in range(len(ID)):                                             #각 항목 별 반복
            wr.writerow([str((i + 1) + (cnt * 50)), ID[i], Title[i], Location[i]]) 
        file.close()


    def scrap(self):
        file = open("indeed.csv", "w",encoding="UTF-8", newline="")         #open(파일명, w, encoding, newline) => w = 파일 열고 새로 쓰기
        wr = csv.writer(file)                                               #csv의 writer객체 인자 = 위에 넣은 정보
        wr.writerow(["No.", "Link", "Title", "Location"])                   #.writerow = 새로 한줄 쓰기 (맨 윗줄에 각 행 별 이름)
        file.close()

        soupPage = self.getHTML(0)                                          #cnt = 0 즉 첫페이지부터 불러와서
        pages = self.getPages(soupPage)                                     #getPagas 함수로 전체 페이지 수 구하기

        for i in range(pages):                                              #전체 페이지 수 만큼 반복
            soupCard = self.getHTML(i)                                      #해당 페이지의 html정보 불러오기
            self.getCards(soupCard, i)                                      #해당 페이지의 html정보내에서 모든 카드 불러오기 (cnt = 해당 페이지 번호)
            print(i+1 , "번쨰 페이지 Done")

if __name__ == "__main__":                                          #해당 모듈이 import되지 않고, interpreter에서 직접 실행 된 경우
    s = Scraper()                                                           # Scraper 매크로의 scrap함수를 실행
    s.scrap()