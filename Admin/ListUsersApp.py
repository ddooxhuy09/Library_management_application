from connect_to_mysql import connect_to_mysql
import mysql.connector
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

class CustomTableWidgetItem(QTableWidgetItem):
    def __init__(self, text):
        super().__init__(text)

    def __lt__(self, other):
        if self.column() == 0:
            return float(self.text()) < float(other.text())
        else:
            return super().__lt__(other)

class ListUsersApp(QWidget):
    def __init__(self):
        super().__init__()

        self.connection = connect_to_mysql()
        self.search_bar_delete = None  
        self.filter_combo_display = None 

        self.init_ui()
        self.load_users()
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
        self.filter_combo_display.addItem("Họ người dùng")
        self.filter_combo_display.addItem("Tên người dùng")
        self.filter_combo_display.addItem("Mã người dùng")
        search_layout_display.addWidget(self.filter_combo_display)

        search_button_display = QPushButton("Tìm kiếm")
        search_layout_display.addWidget(search_button_display)  

        refresh_button_display = QPushButton("Làm mới")
        search_layout_display.addWidget(refresh_button_display)

        search_frame_display.setLayout(search_layout_display)
        layout.addWidget(search_frame_display)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Họ", "Tên", "Email", "Mật khẩu", "Đối tượng", "Ngày tạo"])
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.table)

        button_layout = QHBoxLayout()

        self.delete_button = QPushButton("Xóa người dùng")
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        self.delete_button.clicked.connect(self.delete_user_selected)
        search_button_display.clicked.connect(self.search_users)
        refresh_button_display.clicked.connect(self.refresh_users)

    def load_users(self):
        if not self.connection.is_connected():
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ID, First_name, Last_name, Email, Password, Role, Created_date FROM Users")
            users = cursor.fetchall()

            self.table.setRowCount(len(users))
            for row, user in enumerate(users):
                for col, value in enumerate(user):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, col, item)
        except mysql.connector.Error as err:
            print(f"Lỗi MySQL: {err}")

    def refresh_users(self):
        self.connection = connect_to_mysql()
        self.load_users()

    def search_users(self):
 
        search_text = self.search_bar_display.text()
        filter_option = self.filter_combo_display.currentText()

        if not self.connection.is_connected() or not filter_option or not search_text:
            self.load_users()
            return

        try:
            cursor = self.connection.cursor()
            query = ""

            if filter_option == "Họ người dùng":
                query = "SELECT ID, First_name, Last_name, Email, Password, Role, Created_date FROM Users WHERE First_name LIKE %s"
            elif filter_option == "Tên người dùng":
                query = "SELECT ID, First_name, Last_name, Email, Password, Role, Created_date FROM Users WHERE Last_name LIKE %s"
            elif filter_option == "Mã người dùng":
                query = "SELECT ID, First_name, Last_name, Email, Password, Role, Created_date FROM Users WHERE ID LIKE %s"

            cursor.execute(query, ("%" + search_text + "%",))
            users = cursor.fetchall()

            self.table.setRowCount(len(users))
            for row, user in enumerate(users):
                for col, value in enumerate(user):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, col, item)

        except mysql.connector.Error as err:
            print(f"Lỗi MySQL: {err}")     

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

        if logical_index == 0:
            for row in range(self.table.rowCount()):
                item = self.table.item(row, logical_index)
                self.table.setItem(row, logical_index, CustomTableWidgetItem(item.text()))

    def delete_user_selected(self):
        selected_row = self.table.currentRow()

        if selected_row < 0:
            QMessageBox.critical(self, "Lỗi", "Vui lòng chọn một người dùng để xóa.")
            return

        user_id = self.table.item(selected_row, 0).text()

        confirm = QMessageBox.question(
            self,
            "Xác nhận",
            f"Bạn có chắc chắn muốn xóa người dùng có ID {user_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                db = connect_to_mysql()
                if db is not None:
                    cursor = db.cursor()

                    delete_query = "DELETE FROM Users WHERE ID = %s"
                    cursor.execute(delete_query, (user_id,))
                    db.commit()

                    QMessageBox.information(self, "Thành công", f"Người dùng có ID {user_id} đã được xóa thành công.")
                    
                    self.refresh_users()

            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
            finally:
                db.close()
        else:
            QMessageBox.critical(self, "Lỗi", "Vui lòng chọn một người dùng để xóa.") 