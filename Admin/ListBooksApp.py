from connect_to_mysql import connect_to_mysql
import mysql.connector
import pandas as pd
import sqlalchemy
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QHeaderView,
    QAbstractItemView
)
from BookEditInfoWidget import BookEditInfoWidget

class CustomTableWidgetItem(QTableWidgetItem):
    def __init__(self, text):
        super().__init__(text)

    def __lt__(self, other):
        if self.column() in [0, 6]:
            return float(self.text()) < float(other.text())
        else:
            return super().__lt__(other)

class ListBooksApp(QWidget):
    def __init__(self):
        super().__init__()

        self.connection = connect_to_mysql()
        self.search_bar_delete = None  
        self.filter_combo_display = None  

        self.init_ui()
        self.load_books()
        self.add_sorting_arrows()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        search_frame_display = QWidget()
        search_layout_display = QHBoxLayout()
        search_layout_display.setContentsMargins(0, 0, 0, 0)

        self.search_bar_display = QLineEdit()
        self.search_bar_display.setPlaceholderText("Tìm kiếm")
        search_layout_display.addWidget(self.search_bar_display)

        self.filter_combo_display = QComboBox()
        self.filter_combo_display.addItem("Tên sách")
        self.filter_combo_display.addItem("Tác giả")
        self.filter_combo_display.addItem("Mã sách")
        search_layout_display.addWidget(self.filter_combo_display)

        search_button_display = QPushButton("Tìm kiếm")
        search_layout_display.addWidget(search_button_display)

        refresh_button_display = QPushButton("Làm mới")
        search_layout_display.addWidget(refresh_button_display)

        search_frame_display.setLayout(search_layout_display)
        layout.addWidget(search_frame_display)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(["Mã sách", "Tên Sách", "Thể loại", "Tác giả", "NXB", "Mô tả", "Số lượng", "Giá sách nhập","Đường dẫn ảnh", "Ngày cập nhật"])
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(5, 5, 5, 5)

        self.delete_button = QPushButton("Xóa Sách")
        button_layout.addWidget(self.delete_button)

        self.export_file_button = QPushButton("Xuất ra file")
        button_layout.addWidget(self.export_file_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        self.delete_button.clicked.connect(self.delete_book_selected)
        self.export_file_button.clicked.connect(self.export_file)
        search_button_display.clicked.connect(self.search_books)
        refresh_button_display.clicked.connect(self.refresh_books)

        self.table.itemClicked.connect(self.show_book_details)

    def show_book_details(self, item):
        row = item.row()
        book_id = self.table.item(row, 0).text()
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM Books WHERE ID = %s", (book_id,))
        book_details = cursor.fetchone()

        cursor.execute("SELECT Name FROM Publishers WHERE ID = %s", (book_details[4],))
        publisher_record = cursor.fetchone()

        self.book_info_widget = BookEditInfoWidget(book_id, book_details[1], book_details[2], book_details[3], publisher_record[0], book_details[5], book_details[6], book_details[7], book_details[9])
        self.book_info_widget.setWindowTitle("Thông Tin Sách")
        self.book_info_widget.setGeometry(100, 100, 400, 500)
        self.book_info_widget.show()

    def load_books(self):
        if not self.connection.is_connected():
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT B.ID, B.Name, B.Genre, B.Author, P.Name, B.Description, B.Quantity, B.Price, B.BookImage, B.Update_day 
                FROM Books B
                INNER JOIN Publishers P ON B.Publisher_id = P.ID
            """)
            books = cursor.fetchall()

            self.table.setRowCount(len(books))
            for row, book in enumerate(books):
                for col, value in enumerate(book):  
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, col, item)
        except mysql.connector.Error as err:
            print(f"Lỗi MySQL: {err}")

    def refresh_books(self):
        self.connection = connect_to_mysql()
        self.load_books()
        self.search_bar_display.clear()

    def search_books(self):
        search_text = self.search_bar_display.text()
        filter_option = self.filter_combo_display.currentText()

        if not self.connection.is_connected() or not filter_option or not search_text:
            self.load_books()
            return

        try:
            cursor = self.connection.cursor()
            query = ""

            if filter_option == "Tên sách":
                query = "SELECT ID, Name, Genre, Author, Publisher_id, Description, Quantity, BookImage, Update_day FROM Books WHERE Name LIKE %s"
            elif filter_option == "Tác giả":
                query = "SELECT ID, Name, Genre, Author, Publisher_id, Description, Quantity, BookImage, Update_day FROM Books WHERE Author LIKE %s"
            elif filter_option == "Mã sách":
                query = "SELECT ID, Name, Genre, Author, Publisher_id, Description, Quantity, BookImage, Update_day FROM Books WHERE ID LIKE %s"

            cursor.execute(query, ("%" + search_text + "%",))
            books = cursor.fetchall()

            self.table.setRowCount(len(books))
            for row, book in enumerate(books):
                for col, value in enumerate(book):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, col, item)

        except mysql.connector.Error as err:
            print(f"Lỗi MySQL: {err}")     

    def add_sorting_arrows(self):
        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
            
            header.setSortIndicatorShown(True)
            header.setSortIndicator(col, Qt.SortOrder.AscendingOrder)
            header.sortIndicatorChanged.connect(self.sort_table)

    def sort_table(self, logical_index, order):
        self.table.sortItems(logical_index, order)

        if logical_index in [0, 6]:
            for row in range(self.table.rowCount()):
                item = self.table.item(row, logical_index)
                self.table.setItem(row, logical_index, CustomTableWidgetItem(item.text()))

    def delete_book_selected(self):
            selected_row = self.table.currentRow()
            print (selected_row)
            if selected_row < 0:
                QMessageBox.critical(self, "Lỗi", "Vui lòng chọn một cuốn sách để xóa.")
                return
            
            book_id = self.table.item(selected_row, 0).text()
            print (book_id)
            # Check if the book is currently borrowed or reserved
            if self.is_book_borrowed_or_reserved(book_id):
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa cuốn sách có ID {book_id} vì đang có người mượn hoặc đặt.")
                return

            confirm = QMessageBox.question(
                self,
                "Xác nhận",
                f"Bạn có chắc chắn muốn xóa cuốn sách có ID {book_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                try:
                    db = connect_to_mysql()
                    if db is not None:
                        cursor = db.cursor()

                        delete_query = "DELETE FROM Books WHERE ID = %s"
                        cursor.execute(delete_query, (book_id,))
                        db.commit()

                        QMessageBox.information(self, "Thành công", f"Cuốn sách có ID {book_id} đã được xóa thành công.")
                        
                        self.refresh_books()

                except mysql.connector.Error as err:
                    QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
                finally:
                    db.close()

    def is_book_borrowed_or_reserved(self, book_id):
        try:
            cursor = self.connection.cursor()

            # Check if the book is in Checkouts or Reservations table
            cursor.execute("SELECT * FROM Checkouts WHERE Book_id = %s", (book_id,))
            if cursor.fetchone():
                return True

            cursor.execute("SELECT * FROM Reservations WHERE Book_id = %s", (book_id,))
            if cursor.fetchone():
                return True

        except mysql.connector.Error as err:
            print(f"Lỗi MySQL: {err}")

        return False
    
    def export_file(self):
        if not self.connection.is_connected():
            return

        try:
            query = "SELECT * FROM Books"

            connection_string = f"mysql+mysqlconnector://{self.connection.user}:{self.connection._password}@{self.connection._host}:{self.connection._port}/{self.connection._database}"

            engine = sqlalchemy.create_engine(connection_string)

            df = pd.read_sql(query, con=engine)

            with pd.ExcelWriter("book.xlsx", engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Sheet1', index=False)

            QMessageBox.information(self, "Thành công", "Xuất dữ liệu thành công vào file book.xlsx")

        except mysql.connector.Error as err:
            print(f"Lỗi MySQL: {err}")