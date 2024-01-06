from connect_to_mysql import connect_to_mysql
import mysql.connector
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QImage, QPixmap
from PyQt6.QtWidgets import QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QFileDialog, QInputDialog, QScrollArea, QHeaderView, QTableWidget, QAbstractItemView, QTableWidgetItem
import requests

class BookEditInfoWidget(QWidget):
    def __init__(self, book_id, title, genre, author, publisher, description, quantity, image_path, price):
        super().__init__()
        self.connection = connect_to_mysql()
        self.id_book = book_id
        self.title = title
        self.genre = genre
        self.author = author
        self.publisher = publisher
        self.description = description
        self.quantity = quantity
        self.price = price
        self.image_path = image_path

        self.init_ui()
        self.load_entries()

    def init_ui(self):
        self.setFixedSize(700,500)
        layout = QVBoxLayout()
        
        layout.setContentsMargins(5, 0, 0, 0)
        # layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        

        title_row = QHBoxLayout()
        self.title_label = QLabel(f"Tên Sách: {self.title}")
        self.title_label.setWordWrap(True)
        title_row.addWidget(self.title_label)
        title_row.addStretch()
        self.edit_title_button = QPushButton("")
        self.edit_title_button.setObjectName("edit_title_button")
        self.edit_title_button.setIcon(QIcon('img/edit.png'))
        self.edit_title_button.clicked.connect(lambda: self.edit_property('tên sách'))
        title_row.addWidget(self.edit_title_button)
        layout.addLayout(title_row)

        genre_row = QHBoxLayout()
        self.genre_label = QLabel(f"Thể loại: {self.genre}")
        genre_row.addWidget(self.genre_label)
        genre_row.addStretch()

        self.edit_genre_button = QPushButton("")
        self.edit_genre_button.setObjectName("edit_genre_button")
        self.edit_genre_button.setIcon(QIcon('img/edit.png'))
        self.edit_genre_button.clicked.connect(lambda: self.edit_property('thể loại'))
        genre_row.addWidget(self.edit_genre_button)
        layout.addLayout(genre_row)

        author_row = QHBoxLayout()
        self.author_label = QLabel(f"Tác giả: {self.author}")
        author_row.addWidget(self.author_label)
        author_row.addStretch()
        self.edit_author_button = QPushButton("")
        self.edit_author_button.setObjectName("edit_author_button")

        self.edit_author_button.setIcon(QIcon('img/edit.png'))
        self.edit_author_button.clicked.connect(lambda: self.edit_property('tác giả'))
        author_row.addWidget(self.edit_author_button)
        layout.addLayout(author_row)

        publisher_row = QHBoxLayout()
        self.publisher_label = QLabel(f"NXB: {self.publisher}")
        publisher_row.addWidget(self.publisher_label)
        publisher_row.addStretch()
        self.edit_publisher_button = QPushButton("")
        self.edit_publisher_button.setObjectName("edit_publisher_button")

        self.edit_publisher_button.setIcon(QIcon('img/edit.png'))
        self.edit_publisher_button.clicked.connect(lambda: self.edit_property('NXB'))
        publisher_row.addWidget(self.edit_publisher_button)
        layout.addLayout(publisher_row)

        description_row = QHBoxLayout()
        self.description_label = QLabel(f"Mô tả sách: {self.description}")
        self.description_label.setWordWrap(True)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.description_label)

        scroll_area.setObjectName("description")

        description_row.addWidget(scroll_area)
        description_row.addStretch()
        self.edit_description_button = QPushButton("")
        self.edit_description_button.setObjectName("edit_description_button")

        self.edit_description_button.setIcon(QIcon('img/edit.png'))
        self.edit_description_button.clicked.connect(lambda: self.edit_property('mô tả'))
        description_row.addWidget(self.edit_description_button)
        layout.addLayout(description_row)

        quantity_row = QHBoxLayout()
        self.quantity_label = QLabel(f"Số lượng: {self.quantity}")
        quantity_row.addWidget(self.quantity_label)
        quantity_row.addStretch()

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Số lượng", "Thành tiền", "Ngày cập nhật"])
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.table)

        self.edit_quantity_button = QPushButton("")
        self.edit_quantity_button.setObjectName("edit_quantity_button")

        self.edit_quantity_button.setIcon(QIcon('img/edit.png'))
        self.edit_quantity_button.clicked.connect(lambda: self.edit_property('số lượng'))
        quantity_row.addWidget(self.edit_quantity_button)
        layout.addLayout(quantity_row)
        

        right_layout = QVBoxLayout()
        # right_layout.addStretch()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)


        if self.image_path[0] == 'h':
            image = QImage()
            image.loadFromData(requests.get(self.image_path).content)
        else:
            image = self.image_path

        self.image_label = QLabel()
        pixmap = QPixmap(image)
        if pixmap.isNull():
            print("Lỗi: Không thể tải hình ảnh")
        scaled_pixmap = pixmap.scaled(250, 350)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setScaledContents(True)
        self.image_label.setFixedSize(250, 350)
        right_layout.addWidget(self.image_label)
        
        self.edit_image_button = QPushButton("Sửa hình ảnh")
        self.edit_image_button.clicked.connect(self.update_image)
        right_layout.addWidget(self.edit_image_button)


        # Combine left and right layouts
        main_layout = QHBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(right_layout)
        main_layout.addLayout(layout)
        main_layout2= QVBoxLayout()
        main_layout2.addLayout(main_layout)
        self.save_button = QPushButton("Lưu")
        self.save_button.clicked.connect(self.save_changes)
        main_layout2.addWidget(self.save_button)
        

        self.setLayout(main_layout2)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.book_id = self.id_book
        self.title = None
        self.genre = None
        self.author = None
        self.publisher = None
        self.description = None
        self.quantity_1 = self.quantity
        self.quantity = None
        self.image_path = None
        self.setStyleSheet(open("css/admin.css", encoding="utf-8").read())
    def edit_property(self, property_name):
        new_text, ok = QInputDialog.getText(self, "Sửa thông tin", f"Nhập {property_name} mới:")
        if ok:

            if property_name == 'tên sách':
                self.title = new_text
                self.title_label.setText(f"Tên sách: {new_text}")

            if property_name == 'thể loại':
                self.genre = new_text
                self.genre_label.setText(f"Thể loại: {new_text}")

            if property_name == 'tác giả':
                self.author = new_text           
                self.author_label.setText(f"Tác giả: {new_text}")

            if property_name == 'NXB':
                self.publisher = new_text
                self.author_label.setText(f"NXB: {new_text}")

            if property_name == 'mô tả':
                self.description = new_text
                self.author_label.setText(f"Mô tả sách: {new_text}")

            if property_name == 'số lượng':
                self.quantity = new_text  
                self.author_label.setText(f"Số lượng: {new_text}")

    def update_image(self):
        options = QFileDialog.Option.ReadOnly
        image_file, _ = QFileDialog.getOpenFileName(self, "Chọn Ảnh Sách", "", "Tệp Hình Ảnh (*.png *.jpg *.jpeg *.bmp *.gif);;Tất Cả Tệp (*)", options=options)

        if image_file:
            self.image_path = image_file
            self.selected_image = QPixmap(image_file)
            self.image_label.setPixmap(self.selected_image)
            self.image_label.setScaledContents(True)

    def save_changes(self):
        db = connect_to_mysql()
        cursor = db.cursor()

        if self.title:
            cursor.execute("UPDATE Books SET Name = %s WHERE ID = %s", (self.title, self.book_id))

        if self.genre:    
            cursor.execute("UPDATE Books SET Genre = %s WHERE ID = %s", (self.genre, self.book_id))

        if self.author:    
            cursor.execute("UPDATE Books SET Author = %s WHERE ID = %s", (self.author, self.book_id))

        if self.publisher:
            cursor.execute("SELECT ID FROM Publishers WHERE Name = %s", (self.publisher,))
            publisher_record = cursor.fetchone()
            if publisher_record:
                publisher_id = publisher_record[0]
                cursor.execute("UPDATE Books SET Publisher_id = %s WHERE ID = %s", (publisher_id, self.book_id))
            else:
                insert_publisher_query = "INSERT INTO Publishers (Name, Update_day) VALUES (%s, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 7 HOUR))"
                values = (self.publisher,)
                cursor.execute(insert_publisher_query, values)
                publisher_id = cursor.lastrowid

        if self.description:
            cursor.execute("UPDATE Books SET Description = %s WHERE ID = %s", (self.description, self.book_id))

        if self.quantity:
            cursor.execute("UPDATE Books SET Quantity = %s WHERE ID = %s", (int(self.quantity_1) + int(self.quantity), self.book_id))
            db.commit()

            db = connect_to_mysql()
            cursor = db.cursor()
            sql = "INSERT INTO Entries (ID_Book, Quantity, Price, Update_day) VALUES (%s, %s, %s, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 7 HOUR))"
            values = (self.book_id, self.quantity  ,int(self.price) * int(self.quantity))
            cursor.execute(sql, values)


        if self.image_path:   
            cursor.execute("UPDATE Books SET BookImage = %s WHERE ID = %s", (self.image_path, self.book_id))

        db.commit()
        cursor.close()
        db.close()
        self.close()

    def load_entries(self):
        if not self.connection.is_connected():
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT Quantity, Price, Update_day
                FROM Entries
                WHERE ID_Book = %s
            """,(self.id_book,) )
            books = cursor.fetchall()

            self.table.setRowCount(len(books))
            for row, book in enumerate(books):
                for col, value in enumerate(book):  
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, col, item)
        except mysql.connector.Error as err:
            print(f"Lỗi MySQL: {err}")