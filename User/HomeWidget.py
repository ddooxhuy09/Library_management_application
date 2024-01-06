from connect_to_mysql import connect_to_mysql
import mysql.connector
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QLineEdit,
    QToolButton,
    QScrollArea,
    QMessageBox
)
from PyQt6.QtGui import QPixmap, QIcon, QImage
from PyQt6.QtCore import Qt, QSize, pyqtSignal
import requests

class HomeWidget(QWidget):
    book_info_requested = pyqtSignal(int, str, str, str, str, str, str, int)

    def __init__(self, parent):
        super().__init__(parent)
        self.load_more_button = None
        self.total_books_count = 0
        self.offset_value = 0
        self.search_offset_value = 0
        self.sort_offset_value = 0
        self.connection = connect_to_mysql()

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        widget_content = QWidget()
        layout = QVBoxLayout(widget_content)
        layout.setContentsMargins(10, 0, 0, 0)
        search_layout = QHBoxLayout()

        search_layout.setContentsMargins(0, 0, 0, 0)
        self.search_filter = QComboBox(self)
        self.search_filter.addItems(["Tên sách", "Tác giả", "Thể loại"])
        self.sort_filter = QComboBox(self)
        self.sort_filter.addItems(["A-Z", "Z-A"])
        self.search_input = QLineEdit(self)
        search_button = QPushButton("Tìm", self)
        refresh_button_display = QPushButton("Làm mới", self)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_filter)
        search_layout.addWidget(self.sort_filter)
        search_layout.addWidget(search_button)
        search_layout.addWidget(refresh_button_display)

        layout.addLayout(search_layout)
        self.book_grid_layout = QGridLayout()
        self.load_books()

        layout.addLayout(self.book_grid_layout)
        layout.addStretch(1)

        widget_content.setLayout(layout)
        scroll_area.setWidget(widget_content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        search_button.clicked.connect(self.search_books)
        refresh_button_display.clicked.connect(self.clear_search)

        # self.sort_filter.currentIndexChanged.connect(lambda: self.sort_books(self.sort_filter.currentText()))

    def truncate_text(self, text):
        max_length = 24

        if len(text) > max_length:
            # Check if there is a space within the first 15 characters
            space_index = text.rfind(' ', 0, max_length)
            if space_index != -1:
                # Break the text into two lines at the last space within the first 15 characters
                first_line = text[:space_index]
                second_line = text[space_index + 1:]
            else:
                # If there is no space, truncate to the first 15 characters
                first_line = text[:max_length]
                second_line = ''

            # Return the truncated text with '...' at the end
            return f"{first_line}\n{second_line}"
        else:
            return text

    def display_books(self, books_to_display):
        row = self.book_grid_layout.rowCount()
        col = 0

        for book in books_to_display:
            book_Id, book_name, book_author, book_publisher, book_description, book_genre, book_quantity, book_image = book

            book_button = QToolButton(self)
            book_button.setObjectName("book-button")

        
            if book_image[0] == 'h':
                image = QImage()
                image.loadFromData(requests.get(book_image).content)
            else:
                image = book_image

            pixmap = QPixmap(image)
            if not pixmap.isNull():
                icon_size = QSize(200, 230)
                icon = QIcon(pixmap.scaled(icon_size))
                book_button.setIcon(icon)
                book_button.setIconSize(icon_size)
                book_button.setFixedSize(250, 310)
                book_button.setText(self.truncate_text(book_name))
                book_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
                book_button.clicked.connect(lambda ch, Id=book_Id, title=book_name, image_path=book_image,
                                            quantity=book_quantity, author=book_author, genre=book_genre,
                                            publisher=book_publisher, description=book_description: self.book_info_requested.emit(Id, title, author, str(publisher), genre, description, image_path, quantity))

                self.book_grid_layout.addWidget(book_button, row, col, alignment=Qt.AlignmentFlag.AlignCenter)
                self.total_books_count += 1
            col += 1
            if col == 3:
                row += 1
                col = 0

        if books_to_display:
            if self.total_books_count % 6 == 0 and self.total_books_count != 0:
                #if self.load_more_button is None:
                    self.load_more_button = QPushButton("Tải thêm sách :>", self)
                    self.load_more_button.clicked.connect(self.load_more_books)
                    self.book_grid_layout.addWidget(self.load_more_button, row, col, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        else:
            QMessageBox.information(self, "Không tìm thấy", "Bạn đã đi đến cuối cùng!")  
        

    def load_books(self):
        self.load_filtered_books_active = False
        db = connect_to_mysql()
        if db is None:
            return

        try:
            cursor = db.cursor()
            cursor.execute("""SELECT B.ID, B.Name, B.Author, P.Name, B.Description, B.Genre, B.Quantity, B.BookImage 
                            FROM Books B 
                            INNER JOIN Publishers P ON B.Publisher_id = P.ID
                            LIMIT 6 OFFSET %s""", (self.offset_value,))
            books = cursor.fetchall()
            self.display_books(books)
            self.offset_value += 6
        except mysql.connector.Error as e:
            print("Lỗi:", e)
        finally:
            db.close()

    def load_filtered_books(self, books):
        self.load_filtered_books_active = True
        self.display_books(books)

    def search_books(self):
        self.clear_book_grid_layout()
        search_text = self.search_input.text().strip()
        filter_option = self.search_filter.currentText()

        # Reset the main offset when a new search is initiated
        self.offset_value = 0

        if not search_text:
            self.sort_books(self.sort_filter.currentText())
            return
        self.sort_filter.hide()
        # Clear existing books from the grid layout
        self.clear_book_grid_layout()

        db = connect_to_mysql()
        if db is None:
            return

        try:
            cursor = db.cursor()

            if filter_option == "Tên sách":
                query = "SELECT ID, Name, Author, Publisher_id, Description, Genre, Quantity, BookImage FROM Books WHERE Name LIKE %s LIMIT 6 OFFSET %s"
            elif filter_option == "Tác giả":
                query = "SELECT ID, Name, Author, Publisher_id, Description, Genre, Quantity, BookImage FROM Books WHERE Author LIKE %s LIMIT 6 OFFSET %s"
            elif filter_option == "Thể loại":
                query = "SELECT ID, Name, Author, Publisher_id, Description, Genre, Quantity, BookImage FROM Books WHERE Genre LIKE %s LIMIT 6 OFFSET %s"
            else:
                return

            cursor.execute(query, ("%" + search_text + "%", self.offset_value,))
            books = cursor.fetchall()
            self.load_filtered_books(books)

        except mysql.connector.Error as e:
            print("Lỗi:", e)
        finally:
            db.close()

    def load_more_books(self):
        self.load_more_button.setParent(None)
        if self.search_input.text().strip():
            self.search_offset_value += 6

            db = connect_to_mysql()
            if db is None:
                return

            try:
                cursor = db.cursor()

                filter_option = self.search_filter.currentText()

                if filter_option == "Tên sách":
                    query = "SELECT ID, Name, Author, Publisher_id, Description, Genre, Quantity, BookImage FROM Books WHERE Name LIKE %s LIMIT 6 OFFSET %s"
                elif filter_option == "Tác giả":
                    query = "SELECT ID, Name, Author, Publisher_id, Description, Genre, Quantity, BookImage FROM Books WHERE Author LIKE %s LIMIT 6 OFFSET %s"
                elif filter_option == "Thể loại":
                    query = "SELECT ID, Name, Author, Publisher_id, Description, Genre, Quantity, BookImage FROM Books WHERE Genre LIKE %s LIMIT 6 OFFSET %s"
                else:
                    return

                cursor.execute(query, ("%" + self.search_input.text().strip() + "%", self.search_offset_value,))
                books = cursor.fetchall()
                self.load_filtered_books(books)

            except mysql.connector.Error as e:
                print("Lỗi:", e)
            finally:
                db.close()

        else:
            self.sort_offset_value += 6
            db = connect_to_mysql()
        if db is None:
            return

        try:
            cursor = db.cursor()

            filter_option = self.search_filter.currentText()
            sort_option = self.sort_filter.currentText()

            if filter_option == "Tên sách":
                if sort_option == "Z-A":
                    query = "SELECT ID, Name, Author, Publisher_id, Description, Genre, Quantity, BookImage FROM Books ORDER BY Name DESC LIMIT 6 OFFSET %s"
                elif sort_option == "A-Z":
                    query = "SELECT ID, Name, Author, Publisher_id, Description, Genre, Quantity, BookImage FROM Books ORDER BY Name ASC LIMIT 6 OFFSET %s"
                else:
                    return
            elif filter_option == "Tác giả":             
                if sort_option == "Z-A":
                    query = "SELECT ID, Name, Author, Publisher_id, Description, Genre, Quantity, BookImage FROM Books ORDER BY Author DESC LIMIT 6 OFFSET %s"
                elif sort_option == "A-Z":
                    query = "SELECT ID, Name, Author, Publisher_id, Description, Genre, Quantity, BookImage FROM Books ORDER BY Author ASC LIMIT 6 OFFSET %s"
                else:
                    return
            elif filter_option == "Thể loại":     
                if sort_option == "Z-A":
                    query = "SELECT ID, Name, Author, Publisher_id, Description, Genre, Quantity, BookImage FROM Books ORDER BY Genre DESC LIMIT 6 OFFSET %s"
                elif sort_option == "A-Z":
                    query = "SELECT ID, Name, Author, Publisher_id, Description, Genre, Quantity, BookImage FROM Books ORDER BY Genre ASC LIMIT 6 OFFSET %s"
                else:
                    return
            else:
                return

            cursor.execute(query, (self.sort_offset_value,))
            books = cursor.fetchall()
            self.load_filtered_books(books)

        except mysql.connector.Error as e:
            print("Lỗi:", e)
        finally:
            db.close()

    def clear_book_grid_layout(self):
        self.total_books_count = 0
        # Clear all widgets from the book grid layout
        for i in reversed(range(self.book_grid_layout.count())):
            self.book_grid_layout.itemAt(i).widget().setParent(None)

    def sort_books(self, sort_option):
        self.clear_book_grid_layout()
        self.sort_offset_value = 0
        db = connect_to_mysql()
        if db is None:
            return

        try:
            cursor = db.cursor()

            filter_option = self.search_filter.currentText()

            if filter_option == "Tên sách":
                if sort_option == "Z-A":
                    query = "SELECT ID, Name, Author, Publisher_id, Description, Genre, Quantity, BookImage FROM Books ORDER BY Name DESC LIMIT 6 OFFSET %s"
                elif sort_option == "A-Z":
                    query = "SELECT ID, Name, Author, Publisher_id, Description, Genre, Quantity, BookImage FROM Books ORDER BY Name ASC LIMIT 6 OFFSET %s"
                else:
                    return
            elif filter_option == "Tác giả":             
                if sort_option == "Z-A":
                    query = "SELECT ID, Name, Author, Publisher_id, Description, Genre, Quantity, BookImage FROM Books ORDER BY Author DESC LIMIT 6 OFFSET %s"
                elif sort_option == "A-Z":
                    query = "SELECT ID, Name, Author, Publisher_id, Description, Genre, Quantity, BookImage FROM Books ORDER BY Author ASC LIMIT 6 OFFSET %s"
                else:
                    return
            elif filter_option == "Thể loại":     
                if sort_option == "Z-A":
                    query = "SELECT ID, Name, Author, Publisher_id, Description, Genre, Quantity, BookImage FROM Books ORDER BY Genre DESC LIMIT 6 OFFSET %s"
                elif sort_option == "A-Z":
                    query = "SELECT ID, Name, Author, Publisher_id, Description, Genre, Quantity, BookImage FROM Books ORDER BY Genre ASC LIMIT 6 OFFSET %s"
                else:
                    return
            else:
                return

            cursor.execute(query, (self.offset_value,))
            books = cursor.fetchall()
            self.load_filtered_books(books)

        except mysql.connector.Error as e:
            print("Lỗi:", e)
        finally:
            db.close()

    def clear_search(self):
        self.offset_value = 0
        self.sort_offset_value = 0
        self.search_offset_value = 0
        self.sort_filter.show()
        self.clear_book_grid_layout()
        self.search_input.clear()
        self.load_books()
        self.total_books_count = 0