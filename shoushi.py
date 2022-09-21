from re import X
from tracemalloc import stop
from turtle import pos, pu, up
from attr import NOTHING
import cv2
from cv2 import KeyPoint
import mediapipe as mp 
import time
import math
import threading

from numpy import tri
hands = mp.solutions.hands.Hands()
draw = mp.solutions.drawing_utils
handlmsstyle = draw.DrawingSpec(color = (0,0,255),thickness = 5)
handconstyle = draw.DrawingSpec(color = (0,255,0),thickness = 5)
ctime =0
ptime = 0

def fingerStatus(lmList):
    fingerList = []
    id, originx, originy = lmList[0]
    lx = lmList[5][1]
    rx = lmList[17][1]
    upy = lmList[5][2]
    downy = lmList[17][2]
    if downy > upy:
        tmp = downy
        downy = upy
        upy = tmp
    if lx > rx:
        tmp = lx
        lx = rx 
        rx = tmp
    if (rx-lx) > (upy - downy):
        if lx-20 <= lmList[4][1] <= rx+10:
            fingerList.append(False)
        else:
            fingerList.append(True)
    else:
        if downy-20 <= lmList[4][2] <= upy+10:
            fingerList.append(False)
        else:
            fingerList.append(True)

    keypoint_list = [[6, 8], [10, 12], [14, 16], [18, 20]]
    for point in keypoint_list:
        id, x1, y1 = lmList[point[0]]
        id, x2, y2 = lmList[point[1]]
        if math.hypot(x2-originx, y2-originy) > math.hypot(x1-originx, y1-originy):
            fingerList.append(True)
        else:
            fingerList.append(False)

    return fingerList

def gun(lmList):
    boollist = fingerStatus(lmList)
    lenlist = []
    keypoint_list = [[2,4],[2,8],[4,8]]
    for point in keypoint_list:
        id, x1, y1 = lmList[point[0]]
        id, x2, y2 = lmList[point[1]]
        lenlist.append(math.hypot(y2 - y1,x2 - x1))
    if (math.hypot(lenlist[0],lenlist[1]) + lenlist[2])/2 >=135:
        if not boollist[2] and not boollist[3] and not boollist[4]:
            return True

def Yeah(lmList):
    boollist = fingerStatus(lmList)
    if boollist[1] and boollist[2] and not boollist[3] and not boollist[4] and not boollist[0]:
        return True

def fox(lmList):
    boollist = fingerStatus(lmList)
    lenlist =  []
    keypoint_list = [[4,12],[12,16],[4,16],[8,20]]
    for point in keypoint_list:
        id, x1, y1 = lmList[point[0]]
        id, x2, y2 = lmList[point[1]]
        lenlist.append(math.hypot(y2 - y1,x2 - x1))
    cout = (lenlist[0] + lenlist[1] + lenlist[2]) / 3   
    if boollist[1] and boollist[4]:
        if cout < 60 and (10 < lenlist[3] < 60):
            return True
def good(lmList):
    boollist = fingerStatus(lmList)
    if boollist.count(True) == 1 and boollist[0]:
        return True

def handpose(lmList):
    if gun(lmList):
        print('枪')
    if Yeah(lmList):
        print('Yeah!')
    if fox(lmList):
        print('狐狸！')
    #if good(lmList):
    #    print('Good!')
    time.sleep(1)

def findmax(lmList, diretion = 0):
    ynum = []
    if diretion == 0:
        index2 = 1
    else:
        index2 = 2
    for i in range(len(lmList)):
        ynum.append(lmList[i][index2])
    high = max(ynum)
    low1 = min(ynum)
    ds = high - low1
    return ds

def delay_and_print(message):
    print(message)
    time.sleep(1)

past_hand = []
def changePage(lmlist):
    now_hand = []
    dxlist =[]
    global past_hand
    Fpoint = [8,12,16,20]
    for i in Fpoint:
        now_hand.append(lmlist[i][1])
    if len(past_hand) == 0:
        past_hand = now_hand
    else:
        for j in range(len(past_hand)):
            dx = now_hand[j] - past_hand[j]
            dxlist.append(dx)
        if sum(dxlist)/4 >= 120:
            print("左翻")
        elif sum(dxlist)/4 <= (-120):
            print("右翻")
    past_hand = now_hand
    time.sleep(0.3)


cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)

while True:
    ret,img = cap.read()
    if ret:
        imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        result = hands.process(imgRGB)
        #print(result.multi_hand_landmarks)
        imgHeight = img.shape[0]
        imgWight = img.shape[1]
        if result.multi_hand_landmarks:
            for handlms in result.multi_hand_landmarks:
                draw.draw_landmarks(img,handlms,mp.solutions.hands.HAND_CONNECTIONS,handlmsstyle,handconstyle)
                pos_situation = []
                for i,lm in enumerate(handlms.landmark):
                    xPos = int(lm.x * imgHeight)
                    yPos = int(lm.y * imgWight)
                    pos_situation.append([i, xPos, yPos])
                    #cv2.putText(img,str(i),(xPos+25,yPos+25),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),2)
                if len(threading.enumerate())< 2:
                    t = threading.Thread(target=handpose,args=(pos_situation,))
                    t.start()
                #handpose(pos_situation)

                #print(pos_situation)
                #weight = int(findmax(pos_situation,diretion = 0)) + 40
                #height = int(findmax(pos_situation,diretion = 1))
                #oringalX = int(pos_situation[0][1] + weight/2)+ 80
                #oringalY = int(pos_situation[0][2]) -100
                #cv2.rectangle(img, (oringalX,oringalY),(oringalX - weight, oringalY - height),(0, 255, 0), 2)
        ctime = time.time()
        fps = 1/(ctime-ptime)
        ptime = ctime
        cv2.putText(img,f"FPS:{int(fps)}",(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),3)
        cv2.imshow('img',img)
    if cv2.waitKey(1) == ord('q') :
        break




