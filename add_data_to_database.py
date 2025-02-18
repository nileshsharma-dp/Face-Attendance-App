import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# cred = credentials.Certificate("D:\\Stuff\\Data Science\\Robotics\\Attendance System\\serviceAccountKey.json")
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': 'https://face-attendance-system-6f0dc-default-rtdb.firebaseio.com/'
})

ref = db.reference('Employees')

data = {
    "123456":
    {
        "name": "Ratan Tata",
        "Major" : "Finance",
        "Start_Year" : 2023,
        "total_attendance" : 8,
        "Standing" : "G",
        "Year" : 3,
        "Last_Attendance_Time" : "2023-01-11 11:12:10",
    },
        "234567":
    {
        "name": "Nilesh Sharma",
        "Major" : "Computer Science",
        "Start_Year" : 2024,
        "total_attendance" : 20,
        "Standing" : "M",
        "Year" : 2,
        "Last_Attendance_Time" : "2025-1-1 10:10:10",
    },
        "345678":
    {
        "name": "Narendra Modi",
        "Major" : "Political Science",
        "Start_Year" : 2025,
        "total_attendance" : 9,
        "Standing" : "G",
        "Year" : 1,
        "Last_Attendance_Time" : "2025-1-13 10:10:10",
    },
        "456789":
    {
        "name": "Mukesh Ambani",
        "Major" : "Business Administration",
        "Start_Year" : 2024,
        "total_attendance" : 4,
        "Standing" : "B",
        "Year" : 2,
        "Last_Attendance_Time" : "2024-10-1 10:10:10",
    }
}

for key, value in data.items():
    ref.child(key).set(value)