from connect_to_mysql import connect_to_mysql
import mysql.connector
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QHeaderView,
    QAbstractItemView
)

class CustomTableWidgetItem(QTableWidgetItem):
    def __init__(self, text):
        super().__init__(text)

    def __lt__(self, other):
        if self.column() in [0, 3]:
            return float(self.text()) < float(other.text())
        else:
            return super().__lt__(other)

class ListCheckouts(QWidget):
    def __init__(self):
        super().__init__()

        self.connection = connect_to_mysql()

        self.init_ui()
        self.load_checkout()
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
        self.filter_combo_display.addItem("Mã mượn")
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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID mượn", "Tên sách", "Người dùng", "Số lượng", "Ngày mượn", "Hạn trả", "Ngày trả"])
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.table)

        button_layout = QHBoxLayout()

        self.confirm_button = QPushButton("Xác nhận trả sách")
        button_layout.addWidget(self.confirm_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        search_button_display.clicked.connect(self.search_checkout)
        refresh_button_display.clicked.connect(self.refresh_checkout)
        self.confirm_button.clicked.connect(self.confirm)

    def load_checkout(self):
        if not self.connection.is_connected():
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute(""" 
                            SELECT C.Checkout_id, B.Name, CONCAT(U.First_name, ' ', U.Last_name), C.Quantity, C.Checkout_date, C.Due_date, C.Return_date 
                            FROM Checkouts C
                            INNER JOIN Books B ON C.Book_id = B.ID
                            INNER JOIN Users U ON C.User_id = U.ID
                           """)
            checkouts = cursor.fetchall()

            self.table.setRowCount(len(checkouts))
            for row, checkout in enumerate(checkouts):
                for col, value in enumerate(checkout):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, col, item)
        except mysql.connector.Error as err:
            print(f"Lỗi MySQL: {err}")

    def refresh_checkout(self):
            self.connection = connect_to_mysql()
            self.load_checkout()

    def search_checkout(self):
            search_text = self.search_bar_display.text()
            filter_option = self.filter_combo_display.currentText()

            if not self.connection.is_connected() or not filter_option or not search_text:
                self.load_checkout()
                return

            try:
                cursor = self.connection.cursor()
                query = ""

                if filter_option == "Mã mượn":
                    query = """ 
                                SELECT C.Checkout_id, B.Name, CONCAT(U.First_name, ' ', U.Last_name), C.Quantity, C.Checkout_date, C.Due_date, C.Return_date 
                                FROM Checkouts C
                                INNER JOIN Books B ON C.Book_id = B.ID
                                INNER JOIN Users U ON C.User_id = U.ID
                                WHERE C.Checkout_id LIKE %s
                            """
                elif filter_option == "Tên sách":
                    query = """ 
                                SELECT C.Checkout_id, B.Name, CONCAT(U.First_name, ' ', U.Last_name), C.Quantity, C.Checkout_date, C.Due_date, C.Return_date 
                                FROM Checkouts C
                                INNER JOIN Books B ON C.Book_id = B.ID
                                INNER JOIN Users U ON C.User_id = U.ID
                                WHERE B.Name LIKE %s
                            """
                elif filter_option == "Tên người dùng":
                    query = """ 
                                SELECT C.Checkout_id, B.Name, CONCAT(U.First_name, ' ', U.Last_name), C.Quantity, C.Checkout_date, C.Due_date, C.Return_date 
                                FROM Checkouts C
                                INNER JOIN Books B ON C.Book_id = B.ID
                                INNER JOIN Users U ON C.User_id = U.ID
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

    def confirm(self):
        selected_row = self.table.currentRow()

        if selected_row >= 0:
            checkout_id = int(self.table.item(selected_row, 0).text())

            if not self.connection.is_connected():
                return

            try:
                cursor = self.connection.cursor()

                # Get book_id and quantity from the Checkouts table
                cursor.execute("SELECT Book_id, Quantity FROM Checkouts WHERE Checkout_id = %s", (checkout_id,))
                result = cursor.fetchone()

                if result:
                    book_id, quantity_returned = result

                    # Update the Return_date in the Checkouts table
                    update_query = "UPDATE Checkouts SET Return_date = DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 7 HOUR) WHERE Checkout_id = %s"
                    cursor.execute(update_query, (checkout_id,))
                    self.connection.commit()

                    # Update the quantity in the Books table
                    update_quantity_query = "UPDATE Books SET Quantity = Quantity + %s WHERE ID = %s"
                    cursor.execute(update_quantity_query, (quantity_returned, book_id))
                    self.connection.commit()

                    self.load_checkout()
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