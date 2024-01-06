from connect_to_mysql import connect_to_mysql
import mysql.connector
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QTextEdit,
    QLineEdit,
    QVBoxLayout,QHBoxLayout,
    QWidget,
    QMessageBox,
    QFileDialog
)
from PyQt6.QtGui import QPixmap, QImage
from BookInfoWidget import BookInfoWidget
import pandas as pd
import requests

class AddBookApp(QWidget):
    def __init__(self,list_books_app):
        super().__init__()
        self.list_books_app = list_books_app
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.title_label = QLabel("Tên Sách:")
        self.title_input = QLineEdit()
        layout.addWidget(self.title_label)
        layout.addWidget(self.title_input)

        self.genre_label = QLabel("Thể Loại:")
        self.genre_input = QLineEdit()
        layout.addWidget(self.genre_label)
        layout.addWidget(self.genre_input)

        self.author_label = QLabel("Tác Giả:")
        self.author_input = QLineEdit()
        layout.addWidget(self.author_label)
        layout.addWidget(self.author_input)

        self.publisher_label = QLabel("Nhà xuất bản:")
        self.publisher_input = QLineEdit()
        layout.addWidget(self.publisher_label)
        layout.addWidget(self.publisher_input)

        self.description_label = QLabel("Mô Tả Sách:")
        self.description_input = QTextEdit()
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_input)

        self.quantity_label = QLabel("Số Lượng:")
        self.quantity_input = QLineEdit()
        layout.addWidget(self.quantity_label)
        layout.addWidget(self.quantity_input)

        self.price_label = QLabel("Giá sách:")
        self.price_input = QLineEdit()
        layout.addWidget(self.price_label)
        layout.addWidget(self.price_input)

        self.image_path_label = QLabel("Đường Dẫn Hình Ảnh:")
        self.image_path_input = QLineEdit()
        layout.addWidget(self.image_path_label)
        layout.addWidget(self.image_path_input)

        layout_button = QHBoxLayout()

        self.image_label = QLabel("Hình Ảnh:")
        layout.addWidget(self.image_label)

        self.add_image_button = QPushButton("Chọn Ảnh Sách")
        layout_button.addWidget(self.add_image_button)


        self.add_file_button = QPushButton("Thêm file")
        layout_button.addWidget(self.add_file_button)
        
        self.add_button = QPushButton("Thêm Sách")
        layout_button.addWidget(self.add_button)

        layout.addLayout(layout_button)

        self.setLayout(layout)

        self.add_image_button.clicked.connect(self.add_image)
        self.add_button.clicked.connect(self.add_book)
        self.add_file_button.clicked.connect(self.add_file)
        self.add_button.clicked.connect(self.list_books_app.refresh_books)
        self.selected_image = None
        self.selected_image_path = None
        self.book_info_widget = None
    
    def add_image(self):
        options = QFileDialog.Option.ReadOnly
        image_file, _ = QFileDialog.getOpenFileName(self, "Chọn Ảnh Sách", "", "Tệp Hình Ảnh (*.png *.jpg *.jpeg *.bmp *.gif);;Tất Cả Tệp (*)", options=options)

        if image_file:
            self.selected_image_path = image_file
            self.selected_image = QPixmap(image_file)
            self.image_label.setPixmap(self.selected_image)
            self.image_label.setScaledContents(True)
            self.image_path_input.clear()  # Clear the manual input field when an image is selected

    def add_book(self):
        title = self.title_input.text()
        genre = self.genre_input.text()
        author = self.author_input.text()
        publisher = self.publisher_input.text()
        description = self.description_input.toPlainText()
        quantity_text = self.quantity_input.text()
        price = self.price_input.text()

        try:
            quantity = int(quantity_text)
            if quantity < 0:
                raise ValueError("Số lượng phải lớn hơn hoặc bằng 0")
        except ValueError as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setInformativeText("Vui lòng nhập lại số lượng.")
            msg.setWindowTitle("Lỗi")
            msg.exec()
            return

        if self.selected_image is None and self.image_path_input.text() is None:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setInformativeText("Vui lòng chọn hình ảnh sách.")
            msg.setWindowTitle("Lỗi")
            msg.exec()
            return

        if self.selected_image is None:
            self.selected_image_path = self.image_path_input.text()
            image = QImage()
            image.loadFromData(requests.get(self.selected_image_path).content)
            self.selected_image = QPixmap(image)

        try:
            db = connect_to_mysql()
            if db is not None:
                cursor = db.cursor()

                # Kiểm tra xem nhà xuất bản đã tồn tại trong bảng Publishers hay chưa
                cursor.execute("SELECT ID FROM Publishers WHERE Name = %s", (publisher,))
                publisher_record = cursor.fetchone()

                if publisher_record:
                    publisher_id = publisher_record[0]
                else:

                    insert_publisher_query = "INSERT INTO Publishers (Name, Update_day) VALUES (%s, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 7 HOUR))"
                    values = (publisher,)
                    cursor.execute(insert_publisher_query, values)
                    db.commit()
                    publisher_id = cursor.lastrowid
                
                sql = "INSERT INTO Books (Name, Genre, Author, Publisher_id, Description, Quantity, Price, BookImage, Update_day) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 7 HOUR))"
                values = (title, genre, author, publisher_id, description, quantity, price, self.selected_image_path)
                cursor.execute(sql, values)
                
                db.commit()
                db.close()

                db = connect_to_mysql()
                cursor = db.cursor()
                cursor.execute("""
                    SELECT ID, Quantity, Price
                    FROM Books
                    WHERE BookImage = %s """,(self.selected_image_path,))
                book = cursor.fetchall()

                db = connect_to_mysql()
                cursor = db.cursor()

                sql = "INSERT INTO Entries (ID_Book, Quantity, Price, Update_day) VALUES (%s, %s, %s, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 7 HOUR))"
                values = (book[0][0], book[0][1], book[0][1] * book[0][2])
                cursor.execute(sql, values)
                
                db.commit()
                db.close()

                self.book_info_widget = BookInfoWidget(title, genre, author, publisher, description, quantity, self.selected_image_path)
                self.book_info_widget.setWindowTitle("Thông Tin Sách Đã Thêm")
                self.book_info_widget.setGeometry(100, 100, 400, 500)
                self.book_info_widget.show()

                # Xóa dữ liệu sau khi thêm thành công
                self.title_input.clear()
                self.author_input.clear()
                self.genre_input.clear()
                self.publisher_input.clear()
                self.description_input.clear()
                self.quantity_input.clear()
                self.image_label.clear()
                self.image_path_input.clear()
                self.selected_image = None
                self.selected_image_path = None 
        except mysql.connector.Error as err:
            print(f"Lỗi MySQL: {err}")

    def add_file(self):
        options = QFileDialog.Option.ReadOnly
        path_file, _ = QFileDialog.getOpenFileName(self, "Chọn Ảnh Sách", "", "Tất Cả Tệp (*)", options=options)
        db = connect_to_mysql()
        cursor = db.cursor()

        if path_file:
            df = pd.read_excel(path_file, sheet_name='Sheet1')
            for item in df.iterrows():
                try:
                    title = item[1]["Name"]
                except KeyError:
                    title = None

                try:
                    genre = str(item[1]["Genre"])
                except KeyError:
                    genre = None

                try:
                    author = str(item[1]["Author"])
                except KeyError:
                    author = None

                try:
                    publisher_id = item[1]["Publisher_id"]
                except KeyError:
                    publisher_id = None

                try:
                    description = str(item[1]["Description"])
                except KeyError:
                    description = None

                try:
                    quantity = item[1]["Quantity"]
                except KeyError:
                    quantity = None

                try:
                    selected_image_path = item[1]["BookImage"]
                except KeyError:
                    selected_image_path = None

                sql = "INSERT INTO Books (Name, Genre, Author, Publisher_id, Description, Quantity, BookImage, Update_day) VALUES (%s, %s, %s, %s, %s, %s, %s, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 7 HOUR))"
                values = (title, genre, author, publisher_id, description, quantity, selected_image_path)
                cursor.execute(sql, values)

                db.commit()

            QMessageBox.information(self, "Thành công", "Thêm dữ liệu từ file thành công.")