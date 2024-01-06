import mysql.connector

def connect_to_mysql():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql",
            database="Library"
        )
        return db
    except mysql.connector.Error as err:
        print(f"Lỗi MySQL: {err}")
        return None