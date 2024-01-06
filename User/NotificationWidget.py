from connect_to_mysql import connect_to_mysql
import mysql.connector
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QListWidgetItem,
    QListWidget,
    QPushButton,
    QLabel)
from PyQt6.QtCore import QTimer, QTimer, QDateTime
import datetime

def set_email_user_NotificationWidget(email):
    global email_user
    email_user = email


class NotificationWidget(QWidget):
    def __init__(self, parent, reservation):
        super().__init__(parent)
        self.reservation = reservation
        self.notification_items = []
        self.acknowledged_checkout_notifications = set() 
        self.acknowledged_expiry_notifications = set()


        layout = QVBoxLayout(self)
        self.notification_list = QListWidget(self)
        layout.addWidget(QLabel("Thông báo", self))
        layout.addWidget(self.notification_list)

        clear_button = QPushButton("Xóa thông báo đã xem", self)
        clear_button.clicked.connect(self.clear_notifications)
        layout.addWidget(clear_button)

        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_reservation_time)
        self.timer.timeout.connect(self.check_checkout_time)
        self.timer.timeout.connect(self.check_expiry_time)
        self.timer.start(1000)  # Cập nhật mỗi giây

    def get_user_id(self):
        db = connect_to_mysql()
        
        if db is None:
            return  # Handle the error appropriately

        db = connect_to_mysql()
        cursor = db.cursor()
        cursor.execute("SELECT ID FROM Users WHERE Email = %s", (email_user,))
        user_id = cursor.fetchone()[0]
        db.close()

        return user_id

    def check_reservation_time(self):
        db = connect_to_mysql()
        
        if db is None:
            return  # Handle the error appropriately

        db = connect_to_mysql()
        user_id = self.get_user_id()

        try:
            cursor = db.cursor()

            # Lấy thông tin đặt hàng từ cơ sở dữ liệu
            cursor.execute("SELECT Reservation_id, Book_id, Quantity, Deadline FROM Reservations WHERE Status = 'Đã xác nhận' AND Deadline <= NOW() + INTERVAL 1 DAY AND User_id = %s", (user_id,) )
            results = cursor.fetchall()

            for result in results:
                reservation_id, book_id, quantity, deadline_datetime = result
                deadline_timestamp = datetime.datetime.timestamp(deadline_datetime)
                deadline = QDateTime.fromSecsSinceEpoch(int(deadline_timestamp))
                current_time = QDateTime.currentDateTime()

                # Kiểm tra xem người dùng có thông báo không
                if user_id is not None:
                    # Kiểm tra xem thời hạn đã vượt quá thời gian hiện tại chưa
                    if current_time >= deadline:
                        self.handle_expired_reservation(reservation_id, book_id, quantity)
                        self.show_noti(f"Đặt hàng #{reservation_id} đã quá hạn, đã bị xóa.")
                        self.reservation.refresh()
                    elif current_time.addSecs(2) >= deadline:
                        self.show_noti(f"Bạn còn 2 giây để đi lấy sách. Vui lòng nhanh lên")

        except mysql.connector.Error as e:
            print("Error:", e)
        finally:
            db.close()

    # Các phương thức khác không thay đổi

    def handle_expired_reservation(self, reservation_id, book_id, quantity):
        # Xóa đặt hàng từ bảng Reservations
        db = connect_to_mysql()
        if db is None:
            return

        try:
            cursor = db.cursor()

            # Xóa đặt hàng quá hạn từ bảng Reservations
            cursor.execute("DELETE FROM Reservations WHERE Reservation_id = %s", (reservation_id,))

            # Cộng lại số lượng cho sách tương ứng trong bảng Books
            cursor.execute("UPDATE Books SET Quantity = Quantity + %s WHERE ID = %s", (quantity, book_id))

            db.commit()

        except mysql.connector.Error as e:
            print("Error:", e)
            db.rollback()
        finally:
            db.close()

    def check_checkout_time(self):
        check_check = False
        db = connect_to_mysql()

        if db is None:
            return  # Xử lý lỗi một cách thích hợp

        user_id = self.get_user_id()

        try:
            cursor = db.cursor()

            # Lấy thông tin mượn sách từ cơ sở dữ liệu
            cursor.execute("SELECT Checkout_id, Book_id, Quantity, Due_date FROM Checkouts WHERE User_id = %s AND Return_date IS NULL", (user_id,))
            results = cursor.fetchall()
            
            for result in results:
                checkout_id, book_id, quantity, due_date_datetime = result
                due_date_timestamp = datetime.datetime.timestamp(due_date_datetime)
                due_date = QDateTime.fromSecsSinceEpoch(int(due_date_timestamp))
                current_time = QDateTime.currentDateTime()

                #Kiểm tra xem người dùng có thông báo không
                if user_id is not None:
                    if not self.checkout_notification_acknowledged(checkout_id):
                        if current_time == due_date.addSecs(10):    
                            self.show_noti(f"Mượn sách #{checkout_id} của người dùng #{user_id} đã quá hạn, hãy trả sách ngay.")
                        elif current_time == due_date.addSecs(20): 
                            self.show_noti(f"Mượn sách #{checkout_id} của người dùng #{user_id} đã quá hạn, hãy trả sách ngay.")           
                        elif current_time >= due_date.addSecs(30):    
                            self.show_noti("Bạn đã bị khóa thẻ, vui lòng trả sách để được mở lại!")
                            self.acknowledge_checkout_notification(checkout_id)
                    else:
                        check_check = True 
            
        except mysql.connector.Error as e:
            print("Error:", e)
        finally:
            db.close()

        return check_check
    

    def check_expiry_time(self):
        check_expiry = False
        db = connect_to_mysql()

        if db is None:
            return  # Handle the error appropriately

        user_id = self.get_user_id()

        try:
            cursor = db.cursor()

            # Get card expiry information from the Expiry table
            cursor.execute("SELECT ID, Usage_time, Status, Update_day FROM Expiry WHERE ID = %s", (user_id,))
            results = cursor.fetchall()

            if not results:
                self.add_notification("Bạn chưa đăng ký thẻ mượn. Hãy đăng ký thẻ để mượn sách")
                self.timer.stop()
                check_expiry = True
            else:
                for result in results:
                    expiry_id, usage_time_datetime, status, update_day_datetime = result
                    update_day_timestamp = datetime.datetime.timestamp(update_day_datetime)
                    #update_day = QDateTime.fromSecsSinceEpoch(int(update_day_timestamp))
                    usage_time = QDateTime.fromSecsSinceEpoch(int(usage_time_datetime))
                    current_time = QDateTime.currentDateTime()

                    if not self.expiry_notification_acknowledged(expiry_id):
                        if status == "Còn hạn" and current_time.addSecs(2) == QDateTime.fromSecsSinceEpoch(int(update_day_timestamp)).addSecs(usage_time.toSecsSinceEpoch()):
                            self.show_noti("Còn 2s hết hạn thẻ. Hãy gia hạn sớm!")
                        elif status == "Hết hạn":
                            self.show_noti("Thẻ đã hết hạn. Bạn không thể mượn sách cho đến khi bạn gia hạn thẻ!")
                            self.acknowledge_expiry_notification(expiry_id)
                    else:
                        check_expiry = True  # Notification already acknowledged

        except mysql.connector.Error as e:
            print("Error:", e)
        finally:
            db.close()

        return check_expiry


    def show_noti(self, message):
        if message not in self.acknowledged_checkout_notifications:
            reply = QMessageBox.information(self, "Thông báo", message, QMessageBox.StandardButton.Ok)
            if reply == QMessageBox.StandardButton.Ok:
                self.acknowledged_checkout_notifications.add(message)
            # Thêm thông báo vào danh sách khi nó được hiển thị
            self.add_notification(message)             

    def add_notification(self, message):
        item = QListWidgetItem(message)
        self.notification_list.addItem(item)
        # Lưu thêm item vào danh sách
        self.notification_items.append(item)

    def clear_notifications(self):
        # Xóa các thông báo khỏi danh sách và danh sách hiển thị
        for item in self.notification_items:
            self.notification_list.takeItem(self.notification_list.row(item))
        # Xóa danh sách thông báo
        self.notification_items.clear()

    def closeEvent(self, event):
        # Thực hiện hành động cụ thể trước khi đóng cửa sổ
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có muốn đóng ứng dụng?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Xóa tất cả các thông báo và đóng cửa sổ
            self.clear_notifications()
            event.accept()
        else:
            event.ignore()

    def checkout_notification_acknowledged(self, checkout_id):
        return checkout_id in self.acknowledged_checkout_notifications

    def acknowledge_checkout_notification(self, checkout_id):
        self.acknowledged_checkout_notifications.add(checkout_id)

    def expiry_notification_acknowledged(self, expiry_id):
        return expiry_id in self.acknowledged_expiry_notifications
     
    def acknowledge_expiry_notification(self, expiry_id):
        self.acknowledged_expiry_notifications.add(expiry_id)