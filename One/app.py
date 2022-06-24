import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime,date
import mysql.connector

# import streamlit as st
# import pandas as pd

conn = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="csc_attendance"
)

try:
    print(conn.connection_id)

except:
    print("Connection Failure")

myCursor = conn.cursor()

today = date.today()

path = 'uploads'
images = []
personNames = []
# img_path = []
myList = os.listdir(path)
print(myList)
# reading image and listing
for current_image in myList:
    current_Img = cv2.imread(f'{path}/{current_image}')
    images.append(current_Img)
    personNames.append(os.path.splitext(current_image)[0])
print(personNames)

sql2 = "SELECT * FROM attendance WHERE date = '{}'".format(today)
print(sql2)
# today = date.today()
# print(today)
# val2 = (today)

myCursor.execute(sql2)

myresult1 = myCursor.fetchall()
# myresult2 = []
count = 0
if len(myresult1) == 0:
    print("No data found, on this day: {}".format(today))
    with open('today_attendance.csv', 'w') as f:
        f.writelines("No data found.May be, Attendance has not yet been taken or no one attend school today.")
        f.close()
else:
    for x in myresult1:
        print("Hello World")
        with open('total_attendance.csv', 'a') as f:
            time_now = datetime.now()
            name = x[1]
            status = x[2]
            date = x[3]
            f.writelines(f'\n{name},{status},{date}')
            f.close()

def checkData(name) :
    sql = "SELECT id FROM attendance WHERE (name = %s AND date = %s)"
    # print(today)
    val = (name, today)

    myCursor.execute(sql,val)

    myresult = myCursor.fetchall()
    if len(myresult) == 0:
        saveData(name)
        restoreData(name)
    print(len(myresult))
    print(myresult)

    # for x in myresult:
    #     print(x)
    #     print("Hello World")

def saveData(name) :
    sql = "INSERT INTO attendance (name, status) VALUES (%s, %s)"
    val = (name, 2)
    myCursor.execute(sql, val)
    conn.commit()

def restoreData(name) :
    with open('total_attendance.csv', 'a') as f:
        time_now = date.today()
        name = time_now.strftime('%H:%M:%S')
        status = time_now.strftime('%d/%m/%Y')
        f.writelines(f'\n{name},{status},{time_now}')
        f.close()


# face encoding (find 120 unique points from face)
def faceEncodings(images):
    encodeList = []
    for img in images:
        # print(img) # slf
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

# print(faceEncodings(images))

def attendance(name):
    with open('today_attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            time_now = datetime.now()
            tStr = time_now.strftime('%H:%M:%S')
            dStr = time_now.strftime('%d/%m/%Y')
            f.writelines(f'\n{name},{tStr},{dStr}')
            f.close()


encodeListKnown = faceEncodings(images)
print('All Encodings Complete!!!')

cap = cv2.VideoCapture(1) # external camera
# cap = cv2.VideoCapture(0) # laptop

while True:
    try:
    # x = input()
        ret, frame = cap.read()
        print ('Try using KeyboardInterrupt')
    except KeyboardInterrupt:
        print ('KeyboardInterrupt exception is caught')
    else:
        print ('No exceptions are caught')
    faces = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    faces = cv2.cvtColor(faces, cv2.COLOR_BGR2RGB)

    # find out face location
    facesCurrentFrame = face_recognition.face_locations(faces)
    # find out face encoding
    encodesCurrentFrame = face_recognition.face_encodings(faces, facesCurrentFrame)

    for encodeFace, faceLoc in zip(encodesCurrentFrame, facesCurrentFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        # print(faceDis)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = personNames[matchIndex].upper()
            # print(name)
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            attendance(name)
            checkData(name)

    cv2.imshow('Webcam', frame)
    if cv2.waitKey(1) == 13:
        break

cap.release()
cv2.destroyAllWindows()