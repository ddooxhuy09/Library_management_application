import mysql.connector
import string
from PyQt6.QtWidgets import QMessageBox

def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql",
            database="Library"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def is_valid_password(password):
    if (
        len(password) >= 8 and
        any(char.isupper() for char in password) and
        any(char.isdigit() for char in password) and
        any(char in string.punctuation for char in password)
    ):
        return True
    else:
        return False

def register_user(first_name, last_name, email, password, user_type):

    connection = connect_to_mysql()
    if connection:
        try:
            cursor = connection.cursor()
            insert_query = "INSERT INTO Users (First_name, Last_name, Email, Password, Role, Created_date) VALUES (%s, %s, %s, %s, %s, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 7 HOUR))"
            user_data = (first_name, last_name, email, password, user_type)

            cursor.execute(insert_query, user_data)

            connection.commit()

            cursor.close()
            connection.close()

            print("User registered successfully!")
            return True

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False
    else:
        print("Không thể kết nối đến cơ sở dữ liệu.")
        return False

def reset_password_in_database(email, new_password):
    connection = connect_to_mysql()
    if connection:
        try:
            cursor = connection.cursor()
            update_query = "UPDATE Users SET password = %s WHERE email = %s"
            user_data = (new_password, email)

            cursor.execute(update_query, user_data)

            connection.commit()

            cursor.close()
            connection.close()

            print("Password reset successfully!")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
    else:
        print("Không thể kết nối đến cơ sở dữ liệu.")

def login_user(email, password):
    connection = connect_to_mysql()
    if connection:
        try:
            cursor = connection.cursor()
            select_query = "SELECT * FROM Users WHERE email = %s AND password = %s"
            user_data = (email, password)

            cursor.execute(select_query, user_data)
            user = cursor.fetchone()

            cursor.close()
            connection.close()

            if user:
                print("Login successful!")
                return True
            else:
                print("Login failed. Email or password is incorrect.")
                return False

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False
    else:
        print("Không thể kết nối đến cơ sở dữ liệu.")
        return False

def is_email_exists(email):
    connection = connect_to_mysql()
    if connection:
        try:
            cursor = connection.cursor()
            select_query = "SELECT email FROM Users WHERE email = %s"
            cursor.execute(select_query, (email,))
            result = cursor.fetchone()

            cursor.close()
            connection.close()

            if result:
                return True
            else:
                return False

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False
    else:
        print("Không thể kết nối đến cơ sở dữ liệu.")
        return False
    
def show_info_message(message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setText(message)
    msg.setWindowTitle("Thông báo")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)

    result = msg.exec()

    if result == QMessageBox.StandardButton.Ok:
        pass
