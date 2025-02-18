import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': 'https://face-attendance-system-6f0dc-default-rtdb.firebaseio.com/',
    'storageBucket': 'face-attendance-system-6f0dc.firebasestorage.app'
})

# Load the Employee Images 
folder_path = "Images"
path_list = os.listdir(folder_path)
img_list = []
# print(path_list)
emp_ids = []

for path in path_list:
    lst_img = cv2.imread(f"{folder_path}/{path}")
    img_list.append(lst_img)
    # print(os.path.splitext(path)[0])
    emp_ids.append(os.path.splitext(path)[0])

    file_name = f"{folder_path}/{path}"
    bucket = storage.bucket()
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)


print(emp_ids)
# print(len(img_list))

def find_encodings(imgs_list):
    encoding_list = []
    for img in imgs_list:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encoding_list.append(encode)
    return encoding_list

print("Encoding Started")
encode_list_known = find_encodings(img_list)
encode_list_known_with_ids = [encode_list_known, emp_ids]
print("Encoding Completed")

file = open("encoding_file.pickle", "wb")
pickle.dump(encode_list_known_with_ids, file)
file.close()
print("Encoding File Saved")