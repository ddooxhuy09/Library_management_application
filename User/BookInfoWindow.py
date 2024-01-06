from connect_to_mysql import connect_to_mysql
import mysql.connector
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QGridLayout,
    QPushButton,
    QLabel,
    QTextEdit,
    QInputDialog,
    QScrollArea,
    QStackedWidget
)
from PyQt6.QtGui import QPixmap, QImage
import requests

def set_BookManagementApp(BookApp):
    global BookManagementApp
    BookManagementApp = BookApp

def set_email_user_BookInfoWindow(email):
    global email_user
    email_user = email


class BookInfoWindow(QMainWindow):
    def __init__(self, parent, Id, title, author, publisher, genre, description, image_path, quantity, reservation, notification):
        super().__init__(parent)

        self.notification = notification
        self.reservation = reservation
        self.title = title
        self.Id = Id
        self.quantity = quantity
        self.author = author
        self.publisher = publisher
        self.genre = genre
        self.description = description

        if image_path[0] == 'h':
            image = QImage()
            image.loadFromData(requests.get(image_path).content)
        else:
            image = image_path

        self.image_label = QLabel()
        pixmap = QPixmap(image)
        if pixmap.isNull():
            print("Lỗi: Không thể tải hình ảnh")
        scaled_pixmap = pixmap.scaled(300, 400)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setFixedSize(300, 400)

        self.title_label = QLabel(f"Tên sách: {title}")
        self.title_label.setWordWrap(True)
        self.author_label = QLabel(f"Tác giả: {self.author}")
        self.author_label.setWordWrap(True)
        self.publisher_label = QLabel(f"Nhà xuất bản: {self.publisher}")
        self.publisher_label.setWordWrap(True)
        self.genre_label = QLabel(f"Thể loại: {self.genre}")
        self.genre_label.setWordWrap(True)
        self.description_label = QLabel(f"Mô tả: {self.description}")
        self.description_label.setWordWrap(True)

        self.quantity_label = QLabel(f"Số lượng: {self.quantity}")

        self.borrow_button = QPushButton("Đặt trước")
        self.borrow_button.clicked.connect(self.borrow_book)
        self.borrow_button.clicked.connect(self.reservation.refresh)

        # Add a "Trở về" button
        self.back_button = QPushButton("Trở về")
        self.back_button.clicked.connect(self.go_back)

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.image_label, 0, 0, 6, 1)
        grid_layout.addWidget(self.title_label, 0, 1)
        grid_layout.addWidget(self.author_label, 1, 1)
        grid_layout.addWidget(self.publisher_label, 2, 1)
        grid_layout.addWidget(self.genre_label, 3, 1)
        grid_layout.addWidget(self.description_label, 4, 1)
        grid_layout.addWidget(self.quantity_label, 5, 1)
        grid_layout.addWidget(self.borrow_button, 6, 1)
        grid_layout.addWidget(self.back_button, 7, 1)

        widget = QWidget()
        widget.setLayout(grid_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(widget)  

        self.setCentralWidget(scroll_area)
        self.setMinimumWidth(800)

    def go_back(self):
        # Get the parent widget (QStackedWidget)
        stacked_widget = self.parentWidget()

        # Check if the parent widget is a QStackedWidget
        if isinstance(stacked_widget, QStackedWidget):
            # Set the current index of the QStackedWidget to show the home screen
            stacked_widget.setCurrentIndex(0)  # Assuming 0 is the index of the home screen

    def update_reserve_list(self, user_id, book_id, quantity):
        try:
            db = connect_to_mysql()
            if db is not None:
                cursor = db.cursor()

                Reservation_date = None
                Deadline = None

                #Check if the reservation_id already exists in the table
                cursor.execute("SELECT * FROM Reservations WHERE User_id = %s AND Book_id = %s AND Reservation_date = %s", (user_id, book_id, Reservation_date))
                existing_reservation = cursor.fetchone()

                if existing_reservation:
                    # Update the existing reservation
                    cursor.execute("UPDATE Reservations SET Quantity = Quantity + %s WHERE User_id = %s AND Book_id = %s AND Reservation_date = %s", (quantity, user_id, book_id, Reservation_date))
                    db.commit()
                else:
                    
                    cursor.execute("INSERT INTO Reservations (Book_id, User_id, Quantity, Reservation_date, Deadline, Status) VALUES (%s, %s, %s, %s, %s,'Chưa xác nhận')", (book_id, user_id, quantity, Reservation_date, Deadline))
                    db.commit()

                cursor.close()
                db.close()
        except mysql.connector.Error as err:
            print(f"Lỗi MySQL: {err}")

    def borrow_book(self):
        if self.notification.check_checkout_time():
            QMessageBox.warning(self, "Mượn quá hạn", "Vui lòng trả sách đã bị quá hạn để tiếp tục mượn sách!")
        elif self.notification.check_expiry_time():
            QMessageBox.warning(self, "Thẻ hết hạn", "Bạn không thể mượn sách vì thẻ mượn đã hết hạn hoặc bạn chưa đăng ký thẻ tháng!")
        else:
            if self.quantity > 0:
                total_requested_books = self.reservation.update_total_requested_books() + 1
                if total_requested_books <= 10:
                    self.quantity -= 1
                    self.quantity_label.setText(f"Số lượng còn: {self.quantity}")
                    self.handle_book_borrowed(self.quantity, self.Id)

                    db = connect_to_mysql()
                    cursor = db.cursor()
                    cursor.execute("SELECT ID FROM Users WHERE Email = %s", (email_user,))
                    user_id = cursor.fetchone()[0]
                    self.update_reserve_list(user_id, self.Id, 1)
                else:
                    QMessageBox.warning(self, "Số lượng vượt quá giới hạn", "Bạn chỉ có thể mượn tối đa 10 cuốn sách mỗi lần.")
                
            else:
                self.quantity_label.setText("Hiện tại không có sách để mượn. Quay lại sau.")


    def update_quantity_label(self, new_quantity):
        self.quantity_label.setText(f"Số lượng còn: {new_quantity}")

    def handle_book_borrowed(self, borrowed_quantity, Id):
        try:
            # Thay thế các giá trị dưới đây bằng thông tin kết nối MySQL của bạn.
            db = connect_to_mysql()   
            cursor = db.cursor()

            # Câu lệnh SQL cập nhật số lượng sách
            update_sql = "UPDATE Books SET Quantity = %s WHERE ID = %s"

            # Thực hiện cập nhật
            cursor.execute(update_sql, (borrowed_quantity, Id))
            db.commit()

            # Đóng kết nối và hiển thị thông báo thành công
            cursor.close()
            db.close()
            QMessageBox.information(self, "Thành công", "Mượn sách thành công")
        except mysql.connector.Error as e:
            print("Lỗi cập nhật cơ sở dữ liệu:", e)
            db.rollback()