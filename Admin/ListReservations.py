from connect_to_mysql import connect_to_mysql
import mysql.connector
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QComboBox,
    QLineEdit
)

class CustomTableWidgetItem(QTableWidgetItem):
    def __init__(self, text):
        super().__init__(text)

    def __lt__(self, other):
        if self.column() in [0, 3]:
            return float(self.text()) < float(other.text())
        else:
            return super().__lt__(other)

class ListReservations(QWidget):
    def __init__(self):
        super().__init__()

        self.connection = connect_to_mysql()

        self.init_ui()
        self.load_reservation()
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
        self.filter_combo_display.addItem("Mã đặt trước")
        self.filter_combo_display.addItem("Tên sách")
        self.filter_combo_display.addItem("Tên người dùng")
        search_layout_display.addWidget(self.filter_combo_display)

        search_button_display = QPushButton("Tìm kiếm")
        search_layout_display.addWidget(search_button_display)

        refresh_button_display = QPushButton("Làm mới")
        search_layout_display.addWidget(refresh_button_display)

        search_frame_display.setLayout(search_layout_display)
        layout.addWidget(search_frame_display)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID đặt trước", "Tên sách", "Người dùng", "Số lượng", "Ngày đặt", "Trạng thái"])
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.table)

        button_layout = QHBoxLayout()

        self.confirm_button = QPushButton("Xác nhận đã mượn sách")
        button_layout.addWidget(self.confirm_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        search_button_display.clicked.connect(self.search_reservation)
        refresh_button_display.clicked.connect(self.refresh_reservation)
        self.confirm_button.clicked.connect(self.confirm_user)

    def load_reservation(self):
        if not self.connection.is_connected():
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute(""" 
                            SELECT R.Reservation_id, B.Name, CONCAT(U.First_name, ' ', U.Last_name), R.Quantity, R.Reservation_date, R.Status 
                            FROM Reservations R
                            INNER JOIN Books B ON R.Book_id = B.ID
                            INNER JOIN Users U ON R.User_id = U.ID
                           """)
            reservations = cursor.fetchall()

            self.table.setRowCount(len(reservations))
            for row, reservation in enumerate(reservations):
                for col, value in enumerate(reservation):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, col, item)
        except mysql.connector.Error as err:
            print(f"Lỗi MySQL: {err}")

    def refresh_reservation(self):
        self.connection = connect_to_mysql()
        self.load_reservation()

    def search_reservation(self):
            search_text = self.search_bar_display.text()
            filter_option = self.filter_combo_display.currentText()

            if not self.connection.is_connected() or not filter_option or not search_text:
                self.load_reservation()
                return

            try:
                cursor = self.connection.cursor()
                query = ""

                if filter_option == "Mã đặt trước":
                    query = """ 
                                SELECT R.Reservation_id, B.Name, CONCAT(U.First_name, ' ', U.Last_name), R.Quantity, R.Reservation_date, R.Status 
                                FROM Reservations R
                                INNER JOIN Books B ON R.Book_id = B.ID
                                INNER JOIN Users U ON R.User_id = U.ID
                                WHERE R.Reservation_id LIKE %s
                            """
                elif filter_option == "Tên sách":
                    query = """ 
                                SELECT R.Reservation_id, B.Name, CONCAT(U.First_name, ' ', U.Last_name), R.Quantity, R.Reservation_date, R.Status 
                                FROM Reservations R
                                INNER JOIN Books B ON R.Book_id = B.ID
                                INNER JOIN Users U ON R.User_id = U.ID
                                WHERE B.Name LIKE %s
                            """
                elif filter_option == "Tên người dùng":
                    query = """ 
                                SELECT R.Reservation_id, B.Name, CONCAT(U.First_name, ' ', U.Last_name), R.Quantity, R.Reservation_date, R.Status 
                                FROM Reservations R
                                INNER JOIN Books B ON R.Book_id = B.ID
                                INNER JOIN Users U ON R.User_id = U.ID
                                WHERE U.Last_name LIKE %s
                            """

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


    def confirm_user(self):
        # Lấy dòng được chọn
        selected_row = self.table.currentRow()

        if selected_row >= 0:
            reservation_id = int(self.table.item(selected_row, 0).text())

            cursor = self.connection.cursor()
            cursor.execute("SELECT Book_id, User_id, Quantity FROM Reservations WHERE Reservation_id = %s", (reservation_id,))
            reservations = cursor.fetchall()
            book_id = reservations[0][0]  
            user_id = reservations[0][1]
            quantity = reservations[0][2]
            

            return_date = None

            if not self.connection.is_connected():
                return

            try:
                cursor = self.connection.cursor()
                # Thực hiện truy vấn INSERT vào bảng Checkouts
                cursor.execute("""
                    INSERT INTO Checkouts (Book_id, User_id, Quantity, Checkout_date, Due_date, Return_date)
                    VALUES (%s, %s, %s, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 7 HOUR), DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 175 HOUR), %s)
                """, (book_id, user_id, quantity, return_date))

                self.connection.commit()

                self.table.removeRow(selected_row)

                cursor.execute(" DELETE FROM Reservations WHERE Reservation_id = %s", (reservation_id,))
                self.connection.commit()
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

        if logical_index in [0, 3]:
            for row in range(self.table.rowCount()):
                item = self.table.item(row, logical_index)
                self.table.setItem(row, logical_index, CustomTableWidgetItem(item.text()))