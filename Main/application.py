import cv2
import numpy as np
import face_recognition
import os
from datetime import date


today = date.today()

path = 'uploads'
images = []
studentNames = []
myList = os.listdir(path)
print(myList)
# read image from uploads folder and get names of students
for image in myList:
    current_Img = cv2.imread(f'{path}/{image}')
    images.append(current_Img)
    studentNames.append(os.path.splitext(image)[0])
print(studentNames)

# face encoding (find 120 unique points from face)
def faceEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    print(encodeList)
    return encodeList


def save_collage_attendance(name):
    with open('collage_attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            time_now = today
            tStr = time_now.strftime('%H:%M:%S')
            dStr = time_now.strftime('%d/%m/%Y')
            f.writelines(f'\n{name},{tStr},{dStr}')


encodeListKnown = faceEncodings(images)
print('All Encodings Complete!!!')

# this if for external webcam
# cap = cv2.VideoCapture(1)

# this if for laptop camera
cap = cv2.VideoCapture(0)

while True:
    try:
        ret, frame = cap.read()
        faces = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        faces = cv2.cvtColor(faces, cv2.COLOR_BGR2RGB)

        # find out face location
        facesCurrentFrame = face_recognition.face_locations(faces)
        # find out face encoding
        encodesCurrentFrame = face_recognition.face_encodings(faces, facesCurrentFrame)
    except:
        print('')
    else:
        print('')

    for encodeFace, faceLoc in zip(encodesCurrentFrame, facesCurrentFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        # print(faceDis)
        # print(matches)
        matchIndex = np.argmin(faceDis)
        # print(matchIndex)

        if matches[matchIndex]:
            name = studentNames[matchIndex].upper()
            # print(name)
            # print(faceLoc)
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            save_collage_attendance(name)

    cv2.imshow('Webcam', frame)
    # try:
    if cv2.waitKey(1) == 13:
        break
    # except:
    # else:

cap.release()
cv2.destroyAllWindows()