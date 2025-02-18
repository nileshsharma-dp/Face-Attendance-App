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
import asyncio
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate("D:\\Stuff\\Data Science\\Robotics\\Attendance System\\serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://face-attendance-system-6f0dc-default-rtdb.firebaseio.com/',
    'storageBucket': 'face-attendance-system-6f0dc.firebasestorage.app'
})

bucket = storage.bucket()
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgbackgrnd = cv2.imread(r"D:\Stuff\Data Science\Robotics\Attendance System\Resources\background.png")

folderPath = r"D:\Stuff\Data Science\Robotics\Attendance System\Resources\Modes"
modePathList = os.listdir(folderPath)
imgModeList = []

for path in modePathList:
    lst_img = cv2.imread(f"{folderPath}/{path}")
    imgModeList.append(lst_img)

print("Loading Encoding File Started...")
file = open("encoding_file.pickle", "rb")
encode_list_known_with_ids = pickle.load(file)
file.close()
print("Loading Encoding File Completed")

encode_list_known, emp_ids = encode_list_known_with_ids
id = -1
counter = 0
modeType = 0
img_small = []

async def get_employee_data(id):
    """Get employee data from Firebase asynchronously."""
    ref = db.reference(f"Employees/{id}")
    emp_info = await asyncio.to_thread(ref.get)  # Use to_thread to run blocking calls asynchronously
    return emp_info

async def get_employee_image(id):
    """Get employee image from Firebase Storage asynchronously."""
    blob_path = f"Images/{id}.jpg"
    blob = bucket.get_blob(blob_path)
    if blob is not None:
        array = np.frombuffer(await asyncio.to_thread(blob.download_as_string), np.uint8)
        img_emp = cv2.imdecode(array, cv2.IMREAD_COLOR)
        return img_emp
    else:
        print(f"Image for ID {id} not found in Firebase Storage.")
        return None

async def process_frame(img, modeType, counter, imgbackgrnd):
    """Process the current frame."""
    img = cv2.flip(img, 1)
    img_small = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    img_small = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(img_small)
    encode_cur_frame = face_recognition.face_encodings(img_small, facesCurFrame)

    imgbackgrnd[162:162+480, 55:55+640] = img
    imgbackgrnd[44:44+ 633, 808:808+ 414] = imgModeList[modeType]


    id = -1 
    if facesCurFrame:
        for encode_face, face_Loc in zip(encode_cur_frame, facesCurFrame):
            matches = face_recognition.compare_faces(encode_list_known, encode_face)
            face_dis = face_recognition.face_distance(encode_list_known, encode_face)

            match_index = np.argmin(face_dis)

            if matches[match_index]:
                y1, x2, y2, x1 = face_Loc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55+x1, 162+y1, x2-x1, y2-y1
                imgbackgrnd = cvzone.cornerRect(imgbackgrnd, bbox, 20, rt=0)
                id = emp_ids[match_index]

                if counter == 0:
                    cvzone.putTextRect(imgbackgrnd, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgbackgrnd)
                    cv2.waitKey(1)

                    modeType = 1
                    counter = 1

    return modeType, counter, imgbackgrnd, id

async def main():
    """Main function to run the face attendance system."""
    modeType = 0
    counter = 0
    imgbackgrnd = cv2.imread(r"D:\Stuff\Data Science\Robotics\Attendance System\Resources\background.png")  # Initialize here
    while True:
        bul, img = cap.read()
        if bul:
            modeType, counter, imgbackgrnd, id = await process_frame(img, modeType, counter, imgbackgrnd)

            if counter != 0:
                if counter == 1:
                    emp_info = await get_employee_data(id)
                    print(f"Employee Info: {emp_info}")

                    img_emp = await get_employee_image(id)

                    # Update attendance
                    date_time_object = datetime.strptime(emp_info['Last_Attendance_Time'], "%Y-%m-%d %H:%M:%S")
                    time_now = datetime.now()
                    Seconds_elapsed = (time_now - date_time_object).total_seconds()
                    print(f"Last Attendance Time: {date_time_object} | Current Time: {time_now} | Seconds Elapsed: {Seconds_elapsed}")

                    if Seconds_elapsed > 30:
                        ref = db.reference(f"Employees/{id}")
                        emp_info['total_attendance'] = int(emp_info['total_attendance'] + 1)
                        ref.child('total_attendance').set(emp_info['total_attendance'])
                        ref.child('Last_Attendance_Time').set(time_now.strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        modeType = 3
                        counter = 0
                        imgbackgrnd[44:44+ 633, 808:808+ 414] = imgModeList[modeType]

            cv2.imshow("Face Attendance", imgbackgrnd)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    cap.release()
    cv2.destroyAllWindows()

# Run the main asynchronous function
asyncio.run(main())
