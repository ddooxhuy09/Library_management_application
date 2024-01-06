from connect_to_mysql import connect_to_mysql
import mysql.connector
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QComboBox
)
from PyQt6.QtGui import  QColor

class CustomTableWidgetItem(QTableWidgetItem):
    def __init__(self, text):
        super().__init__(text)

    def __lt__(self, other):
        if self.column() in [0, 2]:
            return float(self.text()) < float(other.text())
        else:
            return super().__lt__(other)

class ExpiryWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.connection = connect_to_mysql()
        
        self.init_ui()
        self.load_expiry()
        self.update_status()
        self.add_sorting_arrows()

    def init_ui(self):
        layout = QVBoxLayout()

        id_time_row_layout = QHBoxLayout()

        self.id_user_label = QLabel("ID người dùng:")
        self.id_user_input = QLineEdit()
        id_time_row_layout.addWidget(self.id_user_label)
        id_time_row_layout.addWidget(self.id_user_input)

        self.time_label = QLabel("Thời gian sử dụng:")
        self.time_input = QLineEdit()
        id_time_row_layout.addWidget(self.time_label)
        id_time_row_layout.addWidget(self.time_input)

        self.add_time_button = QPushButton("Thêm thời gian sử dụng")
        id_time_row_layout.addWidget(self.add_time_button)

        layout.addLayout(id_time_row_layout)

        self.add_time_button.clicked.connect(self.add_time)

        search_frame_display = QWidget()
        search_layout_display = QHBoxLayout()
        search_layout_display.setContentsMargins(0, 0, 0, 0)

        self.search_bar_display = QLineEdit()
        self.search_bar_display.setPlaceholderText("Tìm kiếm")
        search_layout_display.addWidget(self.search_bar_display)

        self.filter_combo_display = QComboBox()
        self.filter_combo_display.addItem("Mã người dùng")
        self.filter_combo_display.addItem("Tên người dùng")
        search_layout_display.addWidget(self.filter_combo_display)

        search_button_display = QPushButton("Tìm kiếm")
        search_layout_display.addWidget(search_button_display)

        refresh_button_display = QPushButton("Làm mới")
        search_layout_display.addWidget(refresh_button_display)

        search_frame_display.setLayout(search_layout_display)
        layout.addWidget(search_frame_display)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID người dùng", "Họ tên", "Thời gian sử dụng", "Trạng thái", "Ngày cập nhật"])
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.table)

        self.setLayout(layout)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        search_button_display.clicked.connect(self.search)
        refresh_button_display.clicked.connect(self.refresh)

    def check_id_exists(self, user_id):
        try:
            db = connect_to_mysql()
            if db is not None:
                cursor = db.cursor()
                query = "SELECT ID FROM Users WHERE ID = %s"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                db.close()
                return result is not None
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        return False
    
    def add_time(self):
        id_user = self.id_user_input.text()
        time = self.time_input.text()

        if not time:
            QMessageBox.critical(self, "Lỗi", "Vui lòng điền đầy đủ thông tin.")
            return
        
        try:
            time = int(time)
        except ValueError:
            QMessageBox.critical(self, "Lỗi", "Giá thuê và phí trễ phải là số nguyên.")
            return

        if not self.check_id_exists(id_user):
            QMessageBox.critical(self, "Lỗi", "ID sách không tồn tại trong bảng.")
            return

        try:
            db = connect_to_mysql()
            if db is not None:
                cursor = db.cursor()

                # Kiểm tra xem ID đã tồn tại và status là "Hết hạn" hay không
                check_sql = "SELECT * FROM Expiry WHERE ID = %s"
                check_values = (id_user,)
                cursor.execute(check_sql, check_values)
                result = cursor.fetchone()

                if result:
                    if result[2] == "Hết hạn":
                        # Nếu ID đã tồn tại và status là "Hết hạn", thì cập nhật lại thời gian và status
                        update_sql = "UPDATE Expiry SET Usage_time = %s, Status = 'Còn hạn', Update_day = DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 7 HOUR) WHERE ID = %s"
                        update_values = (time, id_user)
                        cursor.execute(update_sql, update_values)

                    elif result[2] == "Còn hạn":
                        # Nếu ID đã tồn tại và status là "Còn hạn", thì cộng thêm thời gian vào cột Usage_time
                        update_sql = "UPDATE Expiry SET Usage_time = Usage_time + %s WHERE ID = %s"
                        update_values = (time, id_user)
                        cursor.execute(update_sql, update_values)

                else:
                    # Nếu không, thì thêm mới dữ liệu
                    insert_sql = "INSERT INTO Expiry (ID, Usage_time, Status, Update_day) VALUES (%s, %s, 'Còn hạn', DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 7 HOUR))"
                    insert_values = (id_user, time)
                    cursor.execute(insert_sql, insert_values)

                db.commit()
                db.close()

                QMessageBox.information(self, "Thành công", "Thời gian sử dụng đã được thêm/cập nhật thành công.")

                self.time_input.clear()
                self.id_user_input.clear()
                self.refresh()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")

    def update_status(self):
        try:
            if not self.connection.is_connected():
                return

            cursor = self.connection.cursor()

            update_query = """
                           UPDATE Expiry
                           SET Status = 'Hết hạn'
                           WHERE DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 7 HOUR) >= 
                                 DATE_ADD(Update_day, INTERVAL Usage_time MONTH)
                           """
            cursor.execute(update_query)

            self.connection.commit()
            self.load_expiry()

        except mysql.connector.Error as err:
            print(f"Lỗi MySQL: {err}")

    def load_expiry(self):
        if not self.connection.is_connected():
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute(""" 
                            SELECT E.ID, CONCAT(U.First_name, ' ', U.Last_name), E.Usage_time, E.Status, E.Update_day 
                            FROM Expiry E
                            INNER JOIN Users U ON E.ID = U.ID
                           """)
            expirys = cursor.fetchall()

            self.table.setRowCount(len(expirys))
            for row, expiry in enumerate(expirys):
                for col, value in enumerate(expiry):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, col, item)

                # Set color for expired rows
                status_index = 3  
                status_item = self.table.item(row, status_index)
                if status_item is not None and status_item.text() == 'Hết hạn':
                    status_item.setForeground(QColor('red'))

        except mysql.connector.Error as err:
            print(f"Lỗi MySQL: {err}")

    def search(self):
        search_text = self.search_bar_display.text()
        filter_option = self.filter_combo_display.currentText()

        if not self.connection.is_connected() or not filter_option or not search_text:
            self.load_expiry()
            return

        try:
            cursor = self.connection.cursor()
            query = ""

            if filter_option == "Mã người dùng":
                query = """
                            SELECT E.ID, CONCAT(U.First_name, ' ', U.Last_name), E.Usage_time, E.Status, E.Update_day 
                            FROM Expiry E
                            INNER JOIN Users U ON E.ID = U.ID
                            WHERE E.ID LIKE %s
                           """

            elif filter_option == "Tên người dùng":
                query = """ 
                            SELECT E.ID, CONCAT(U.First_name, ' ', U.Last_name), E.Usage_time, E.Status, E.Update_day 
                            FROM Expiry E
                            INNER JOIN Users U ON E.ID = U.ID
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

    def refresh(self):
        self.connection = connect_to_mysql()
        self.load_expiry()

    def add_sorting_arrows(self):
        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
            
            # Thêm mũi tên sắp xếp lên tiêu đề cột
            header.setSortIndicatorShown(True)
            header.setSortIndicator(col, Qt.SortOrder.AscendingOrder)
            header.sortIndicatorChanged.connect(self.sort_table)

    def sort_table(self, logical_index, order):
        self.table.sortItems(logical_index, order)

        if logical_index in [0, 2]:
            for row in range(self.table.rowCount()):
                item = self.table.item(row, logical_index)
                self.table.setItem(row, logical_index, CustomTableWidgetItem(item.text()))