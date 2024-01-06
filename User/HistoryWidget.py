from connect_to_mysql import connect_to_mysql
import mysql.connector
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView
)
from PyQt6.QtCore import Qt

def set_email_user_HistoryWidget(email):
    global email_user
    email_user = email

class HistoryWidget(QWidget):
    def __init__(self,parent):
        super().__init__(parent)
        
        self.connection = connect_to_mysql()
        self.init_ui()
        self.load_books()    

    def init_ui(self):
        layout=QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Tên sách" , "Số lượng" , "Ngày mượn", "Hạn trả", "Ngày trả"])
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.table)

        self.setLayout(layout)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    def load_books(self):
        if not self.connection.is_connected():
            return

        db = connect_to_mysql()
        cursor = db.cursor()

        # Retrieve user ID based on the email
        cursor.execute("SELECT ID FROM Users WHERE Email = %s", (email_user,))
        user_id = cursor.fetchone()[0]

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT B.Name, C.Quantity, C.Checkout_date, C.Due_date, C.Return_date
                FROM Checkouts C
                INNER JOIN Books B ON C.Book_id = B.ID
                INNER JOIN Users U ON C.User_id = U.ID
                WHERE U.ID = %s
            """, (user_id,))

            books = cursor.fetchall()

            self.table.setRowCount(len(books))
            for row, book in enumerate(books):
                for col, value in enumerate(book):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, col, item)
        except mysql.connector.Error as err:
            print(f"Lỗi MySQL: {err}")