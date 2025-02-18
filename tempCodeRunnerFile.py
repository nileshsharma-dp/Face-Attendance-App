import cv2
import numpy as np
import os
import pickle
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("D:\\Stuff\\Data Science\\Robotics\\Attendance System\\serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': 'https://face-attendance-system-6f0dc-default-rtdb.firebaseio.com/',
    'storageBucket': 'face-attendance-system-6f0dc.firebasestorage.app'
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgbackgrnd = cv2.imread(r"D:\Stuff\Data Science\Robotics\Attendance System\Resources\background.png")

# Load the Mode Images 
folderPath = r"D:\Stuff\Data Science\Robotics\Attendance System\Resources\Modes"
modePathList = os.listdir(folderPath)
imgModeList = []
# print(modePathList)
for path in modePathList:
    lst_img = cv2.imread(f"{folderPath}/{path}")
    imgModeList.append(lst_img)
# print(len(imgModeList))

# load the encoding file
print("Loading Encoding File Started...")
file = open("encoding_file.pickle", "rb")
encode_list_known_with_ids = pickle.load(file)
file.close()
print("Loading Encoding File Completed")
encode_list_known, emp_ids = encode_list_known_with_ids
# encode_list_known = encode_list_known_with_ids[0]
# emp_ids = encode_list_known_with_ids[1]
# print(encode_list_known)
# print(emp_ids)
id = -1
counter = 0
modeType = 0
img_small = []

while True:
    bul, img = cap.read()
    if bul:
        img = cv2.flip(img, 1) # Flip the image
        img_small = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        img_small = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(img_small)
        encode_cur_frame = face_recognition.face_encodings(img_small, facesCurFrame)

        imgbackgrnd[162:162+480, 55:55+640] = img # Replace the background image with the webcam feed
        imgbackgrnd[44:44+ 633, 808:808+ 414] = imgModeList[modeType] # Replace the Mode Image with the webcam feed

        for encode_face, face_Loc in zip(encode_cur_frame, facesCurFrame):
            matches = face_recognition.compare_faces(encode_list_known, encode_face)
            face_dis = face_recognition.face_distance(encode_list_known, encode_face)
            # print("Matches: ", matches)
            # print("Face Distance: ",face_dis)

            match_index = np.argmin(face_dis)
            # print("Match Index: ", match_index)

            if matches[match_index]:
                # print("Match Found")
                # print(emp_ids[match_index])
                y1,x2,y2,x1 = face_Loc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55+x1,162+y1,x2-x1,y2-y1
                imgbackgrnd = cvzone.cornerRect(imgbackgrnd, bbox ,20, rt=0)
                # cvzone.cornerRect(imgbackgrnd, [face_Loc[3]*4, face_Loc[0]*4, face_Loc[1]*4, face_Loc[2]*4], 20, rt=0)
                id = emp_ids[match_index]

                if counter == 0:
                    counter = 1
                    modeType = 1
        if counter != 0:
            if counter == 1:
                # Get the Data from the Firebase
                emp_info = db.reference(f"Employees/{id}").get()
                print(f"Employee Info: {emp_info}")

                # Get the Data from the Firebase Storage
                blob_path = f"Images/{id}.jpg"
                print(f"Looking for image at: {blob_path}")
                blob = bucket.get_blob(blob_path)

                if blob is not None:  # Check if the blob exists
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    img_emp = cv2.imdecode(array, cv2.IMREAD_COLOR)
                else:
                    print(f"Image for ID {id} not found in Firebase Storage.")
        

                # Update data of attendance
                date_time_object = datetime.strptime(emp_info['Last_Attendance_Time'], "%Y-%m-%d %H:%M:%S")
                time_now = datetime.now()
                Seconds_elapsed = (time_now - date_time_object).total_seconds() 
                print(f"Last Attendance Time: {date_time_object}")
                print(f"Current Time: {time_now}")
                print(f"Seconds Elapsed: {Seconds_elapsed}")

                ref = db.reference(f"Employees/{id}")
                emp_info['total_attendance'] = int(emp_info['total_attendance']+1)
                ref.child('total_attendance').set(emp_info['total_attendance'])
            if 10 < counter < 20:
                modeType = 2
                imgbackgrnd[44:44+ 633, 808:808+ 414] = imgModeList[modeType]

            if counter <= 10:
                cv2.putText(imgbackgrnd, str(emp_info['total_attendance']), (861,125), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2) 
                cv2.putText(imgbackgrnd, str(emp_info['Standing']), (910,625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 2)
                cv2.putText(imgbackgrnd, str(id), (1006,493), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 2)
                cv2.putText(imgbackgrnd, str(emp_info['Major']), (1006,550), cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 2)
                cv2.putText(imgbackgrnd, str(emp_info['Year']), (1025,625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 2)
                cv2.putText(imgbackgrnd, str(emp_info['Start_Year']), (1125,625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 2)

                (w, h), _ = cv2.getTextSize(emp_info['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 2)
                offset = (414-w)//2

                cv2.putText(imgbackgrnd, str(emp_info['name']), (808+offset,445), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 2)

                imgbackgrnd[175:175+216,909:909+216] = img_emp
        counter += 1

        if counter >= 20:
            counter = 0
            modeType = 0
            emp_info = []
            img_emp = []
            imgbackgrnd[44:44+ 633, 808:808+ 414] = imgModeList[modeType]

        # cv2.imshow("Image", img)
        cv2.imshow("Face Attendance", imgbackgrnd) # Show the Background Image
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()

