#할일
# 1. File Path 설정 및 Fuzzer bassic-setting
# 2. Sample file pick
# 3. Mutate sample file
# 4. Run, clean, monitor, send email
#fuzzer만들기 매뉴얼:   http://blog.naver.com/PostView.nhn?blogId=cme1245&logNo=221318567610&redirect=Dlog&widgetTypeCall=true&directAccess=false
#os를 포함한 외장 함수: https://wikidocs.net/33
# -*- coding: utf-8 -*-

import random
import math
import os, sys
import threading
import glob
import time
#import utils
import shutil
from datetime import datetime
import gc
import subprocess
# for email
import smtplib
import signal


FUZZ_DELAY = 6
USE_WINDBG = False 
EXPLOITABLE_FRE = 6

class File_Fuzzer:
    def __init__(self,target ,ext):   #기본 경로 설정 => 들어온 1st arg = target, 2nd arg = ext로 들어감
                                                                            #os.path                   = 파일 경로를 생성/수정 하고 파일정보를 쉽게 다루게 해주는 모듈
        self.base_path = os.getcwd() + "/"                                  #os.path.getcwd()          = 현재 자신의 디렉토리 위치 반환
        self.target =target                                                 #target을 self의 객체로 저장
        self.target_path = self.base_path + os.path.basename(target) + "/"  #os.path.basename(절대경로) = 주어진 절대경로의 기본이름(basename)을 반환 = 해당 실행파일 이름 반환하고 그걸 디렉토리 명으로 사용
        self.sample_path = self.base_path + "samples/"                      #base_path에 samples 폴더 생성 (실제로는 해당 경로 저장)
        self.test_path = self.target_path + "test/"                         #target_path에 test 폴더 생성
        self.crash_path = self.target_path +  "crash/"                      #target_path에 crash 폴더 생성
        self.exploitable_path = self.target_path + "crash/exploitable/"     #crash 폴더 안에 exploitable 폴더 생성
        self.sample_ext = ext                                               #ext를 self의 객체로 저장

        self.sample_stream = None
        self.case_name = None
        self.crash_fname = ''
        self.iter = 0
        self.running = False
        self.crash_count = 0
        self.dbg = None
        self.mutate_method = ""
        self.mutate_byte = ""
        self.mutate_offset = 0
        self.mutate_len = 0
        self.orig_bytes = ""
        self.exploitable_count = 0
        self.exploitable_hashset = []
        self.title_exploitable_count = 0
        self.title_probably_exploitable_count = 0

        
        if not os.path.exists(self.target_path):                            #만일 해당 경로에 디렉토리가 존재X면
            os.mkdir(self.target_path)                                      #os.mkdir 해당 경로에 디렉토리 생성
        if not os.path.exists(self.sample_path):                            #순차적으로 target, sample, test, crash, exploitable용 폴더 생성
            os.mkdir(self.sample_path)
        if not os.path.exists(self.test_path):
            os.mkdir(self.test_path)
        if not os.path.exists(self.crash_path):
            os.mkdir(self.crash_path)
        if not os.path.exists(self.exploitable_path):
            os.mkdir(self.exploitable_path)
    
    #샘플파일 미리 삽입 필요?????
    
    def File_Picker(self):            #sample폴더에 존재하는 샘플 파일들 중 랜덤하게 하나의 파일을 선택
        sample_list = glob.glob(self.sample_path + self.sample_ext + '/*')          #glob.glob(경로)    = 해당 경로의 파일목록을 list의 형태로 반환하는 모듈
                                                                                    #/*                 = 해당 디렉토리의 모든 파일
        if len(sample_list) < 1:                                                    #sample_list에 아무것도 담기지 않았다면
            print (" [-] 샘플이 존재하지 않습니다. sample 폴더를 확인해 주세요.")       #오류 메시지 출력
            sys.exit()
        while 1:                                                                    #참이므로 항상 실행
            sample = random.choice(sample_list)                                     #random.choice()     = 이미 있는 데이터 집합에서 일부를 무작위로 선택 https://datascienceschool.net/view-notebook/8bf41f87a08b4c44b307799577736a28/
            self.sample_stream = open(sample,"rb").read()                           #open(경로).read()   = 해당 파일을 rb모드로 열고 읽기
                                                                                    #rb                  = 읽기모드 + 바이너리 모드(바이트 단위 데이터 읽기/기록)
            # print(self.sample_stream[0:10])                                       #테스트용 코드
            if len(self.sample_stream) > 1:                                         #sample_stream에 저장이 된 경우, 반복문 탈출
                break                                                               
        return

    def Mutate(self):                 #선택된 샘플파일을 변형한다
        global mutated_stream 
        global mutate_byte
        test_cases = [ "\x00", "\xff", "\x41", "%%s"]                       #문자 목록(기본)

        case = random.randint(0, 1)                                        #random.randint(최소,최대)  = 범위 내의 임의의 정수 반환
        # case 0 : 값을 랜덤하게 변경한다.  (replace)
        # case 1 : 값을 랜덤하게 삽입한다.  (insert)
      #mutate_count = int(random.randint(1, len(self.sample_stream)) * 0.005)+1 # 전체 변경 바이트 수
        mutate_count = random.randint(1,2)                                  #mutate 반복 횟수 설정      = random.randint(최소,최대)  = 범위 내의 임의의 정수 반환
      #test_cases.append(str(random.randint(0,255)))                        #?

        mutate_byte = random.choice(test_cases)                             #변형바이트 선택            = test_case중 하나 랜덤하게 선택
        self.mutate_byte = mutate_byte                                      #선택한 변형바이트 self의 객체로 저장

        if case == 0: #replace방식
            print (" [+] Case 1. Byte Replace  ")                           
            self.mutate_case = 0                                            #선택된 방식을 self의 객체로 저장
            for i in range(mutate_count):                                   #설정된 mutate횟수 만큼 반복
                mutate_offset = random.randint(1, len(self.sample_stream))  #변경 offset(시작 위치)     = 샘플의 전체 바이너리stream중 하나를 임의로 선택 
                mutate_len = random.randint(1,500)                          #번경 할 부분의 길이        = 1~4중 임의의 숫자 
                mutated_stream = self.sample_stream[0:mutate_offset]        #변경안할부분               = 샘플의 첫 바이너리 부터 offset까지
                
                temp = []
                for i in range (mutate_len):                                #전체 변경길이 만큼 반복
                    temp.append(self.mutate_byte)                           #temp.append(삽입내용)       = temp리스트의 마지막에 arg 삽입
                temp = "".join(temp)                                        #"추가내용".join(리스트)     = 리스트를 문자열(string)으로 변환하여 반환

                ms = bytearray(mutated_stream)                              #변경위치 앞 부분 (bytearray()= 1바이트 단위 값을 연속적으로 저장하는 시퀀스 자료형(bytes와 달리 요소 수정 가능)
                ms += temp.encode()                                         #변경 할 부분 (.encode       = Unicode를 byte열로 변경)
                ms += self.sample_stream[mutate_offset + mutate_len:]       #변경위치 뒷 부분

                print (" [+] Mutated %d counts(replace %d bytes)" % (mutate_count, mutate_len)) #변경된 횟수와 회당 바이트 길이 출력

        else: #insert 방식
            print (" [+] Case 2. Byte Insertion ")                          
            self.mutate_case = 1                                            #선택된 방식을 self의 객체로 저장
            mutate_offset = random.randint(1, len(self.sample_stream))      #변경 offset(시작 위치)     = 샘플의 전체 바이너리stream중 하나를 임의로 선택 
            mutate_len = random.randint(1,500)                              #번경 할 부분의 길이        = 1~4중 임의의 숫자 
            mutated_stream = self.sample_stream[0:mutate_offset]            #변경안할부분               = 샘플의 첫 바이너리 부터 offset까지
            
            #mutated_stream += mutate_byte * mutate_len
            temp = []
            for i in range (mutate_len):                                    #전체 변경길이 만큼 반복
                temp.append(self.mutate_byte)                               #temp.append(삽입내용)       = temp리스트의 마지막에 arg 삽입
            temp = "".join(temp)                                            #"추가내용".join(리스트)     = 리스트를 문자열(string)으로 변환하여 반환
            
            ms = bytearray(mutated_stream)                                  #삽입위치 앞 부분 (bytearray()= 1바이트 단위 값을 연속적으로 저장하는 시퀀스 자료형(bytes와 달리 요소 수정 가능)
            ms += temp.encode()                                             #삽입 할 부분 (.encode       = Unicode를 byte열로 변경)
            ms += self.sample_stream[mutate_offset:]                        #삽입위치 뒷 부분

            print ("  [+] Mutated %d bytes(add)" % (mutate_len) )           #삽입된 바이트 길이 출력

        self.mutate_offset = mutate_offset                                  #변경시작위치/삽입위치를 self의 객체로 저장
        self.case_name = self.test_path + "case-%s.%s" % (str(self.iter),self.sample_ext)
                                                                            #test폴더에 case-0.형식자 파일 생성

        f = open(self.case_name ,"wb")                                      #변경하고자 하는 파일을 wb모드(쓰기모드+2진모드)로 열기
        f.write(bytes(ms))                                                  #ms(변경/삽입하고자하는 바이트)를 파일에
        f.close()
        return 

    def Fuzzing(self, count):
        self.count = count
        print (self.count)
        self.File_Picker()
        self.Mutate()

if __name__ == '__main__':
    print ("Usage example : C:/Users/5ddish/Desktop/fuzzer/reader/reader.exe , zip")    #사용법 출력

    if len(sys.argv) !=3:
        print ("[SYSTEM] Error .... Please Chqeck Usage")                               #2개의 arg가 들어오지 않을 경우 ERROR_MSG 출력
        sys.exit()                                                                      #후 프로그램 종료

    print ("[SYSTEM] Fuzzer Start ")                                                    #프로그램 시작함을  출력으로 표시

    fuzzer = File_Fuzzer(sys.argv[1], sys.argv[2])                                      #arg2개를 넣은 File_Fuzzer 클래스를 fuzzer에 삽입
    fuzzer.Fuzzing(5000)                                                                #fuzzer, 즉, File_Fuzzer 클래스의 Fuzzling 함수 실행