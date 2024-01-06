from connect_to_mysql import connect_to_mysql
import mysql.connector
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QPushButton, 
    QTableWidget,
    QTableWidgetItem,
    QInputDialog,
    QHeaderView,
    QAbstractItemView,
    QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

def set_email_user_ReserveListWidget(email):
    global email_user
    email_user = email

class ReserveListWidget(QWidget):
    quantity_updated = pyqtSignal(int)
    def __init__(self,parent):
        super().__init__(parent)
        
        self.total_requested_books = 0
        self.connection = connect_to_mysql()
        self.init_ui()
        self.load_reserve() 
        self.update_total_requested_books()

    def init_ui(self):
        
        layout=QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Mã đặt sách", "Tên sách", "Số lượng" , "Ngày đặt" , "Hạn lấy", "Trạng thái"])
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.table)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout_button = QHBoxLayout()

        request_button = QPushButton("Yêu cầu")
        request_button.clicked.connect(self.update_total_requested_books)
        request_button.clicked.connect(self.confirm_book)
        layout_button.addWidget(request_button)

        edit_button = QPushButton("Chỉnh sửa")
        edit_button.clicked.connect(self.update_quantity_in_database)
        layout_button.addWidget(edit_button)

        delete_button = QPushButton("Xóa")
        delete_button.clicked.connect(self.delete_reservation)
        layout_button.addWidget(delete_button)
        layout.addLayout(layout_button)

        self.setLayout(layout) 
    def delete_reservation(self):
        selected_rows = self.table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(self, "Chưa chọn hàng", "Vui lòng chọn một hàng để xóa.")
            return

        selected_row = selected_rows[0].row()
        status = self.table.item(selected_row, 5).text()

        if status == 'Đã xác nhận':
            QMessageBox.warning(self, "Lỗi", "Chỉ có thể xóa đặt trước có trạng thái 'Chưa xác nhận'.")
            return

        reservation_id = self.table.item(selected_row, 0).text()

        reply = QMessageBox.question(
            self,
            "Xác nhận xóa đơn đặt sách",
            f"Bạn có thực sự muốn xóa đơn đặt sách #{reservation_id} không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.connection.cursor()

                cursor.execute("SELECT Book_id, Quantity FROM Reservations WHERE Reservation_id = %s", (reservation_id,))
                book_id, quantity = cursor.fetchone()

                cursor.execute("DELETE FROM Reservations WHERE Reservation_id = %s", (reservation_id,))

                cursor.execute("UPDATE Books SET Quantity = Quantity + %s WHERE ID = %s", (quantity, book_id))

                self.connection.commit()
                cursor.close()

                self.load_reserve()
            except mysql.connector.Error as err:
                print(f"Lỗi MySQL: {err}")

    def update_quantity_in_database(self):
        selected_rows = self.table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(self, "Chưa chọn hàng", "Vui lòng chọn một hàng để chỉnh sửa.")
            return

        selected_row = selected_rows[0].row()
        status = self.table.item(selected_row, 5).text()

        if status == 'Đã xác nhận':
            QMessageBox.warning(self, "Lỗi", "Chỉ có thể chỉnh sửa đặt trước có trạng thái 'Chưa xác nhận'.")
            return

        new_quantity, ok = QInputDialog.getInt(self, "Chỉnh sửa số lượng", "Nhập số lượng mới:", 1, 1, 100)

        if ok:
            try:
                reservation_id = self.table.item(selected_row, 0).text()
                status = self.table.item(selected_row, 5).text()

                if status == 'Chưa xác nhận':
                    cursor = self.connection.cursor()

                    cursor.execute("SELECT Quantity FROM Books WHERE ID = (SELECT Book_id FROM Reservations WHERE Reservation_id = %s)", (reservation_id,))
                    old_quantity = int(cursor.fetchone()[0])

                    cursor.execute("UPDATE Reservations SET Quantity = %s WHERE Reservation_id = %s", (new_quantity, reservation_id))
                    
                    initial_quantity = int(self.table.item(selected_row, 2).text())

                    remaining_quantity = initial_quantity + old_quantity - new_quantity
                    
                    cursor.execute("UPDATE Books SET Quantity = %s WHERE ID = (SELECT Book_id FROM Reservations WHERE Reservation_id = %s)", (remaining_quantity, reservation_id))
                    
                    self.connection.commit()
                    cursor.close()

                    self.load_reserve()

                    return remaining_quantity
            except mysql.connector.Error as err:
                print(f"Lỗi MySQL: {err}")

    def load_reserve(self):
        if not self.connection.is_connected():
            return

        db = connect_to_mysql()
        cursor = db.cursor()
        cursor.execute("SELECT ID FROM Users WHERE Email = %s",(email_user,))
        user_id = cursor.fetchone()[0]

        try:
            cursor = self.connection.cursor()
            cursor.execute("""SELECT R.Reservation_id, B.Name, R.Quantity, R.Reservation_date, R.Deadline, R.Status
                           FROM Reservations R
                           INNER JOIN Books B ON R.Book_id = B.ID
                           WHERE R.User_id = %s""", (user_id,))

            books = cursor.fetchall()

            self.table.setRowCount(len(books))
            for row, book in enumerate(books):
                for col, value in enumerate(book):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, col, item)
        except mysql.connector.Error as err:
            print(f"Lỗi MySQL: {err}")

    

    def update_total_requested_books(self):
        db = connect_to_mysql()
        cursor = db.cursor()
        cursor.execute("SELECT ID FROM Users WHERE Email = %s", (email_user,))
        user_id = cursor.fetchone()[0]
        
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT SUM(Quantity) FROM Reservations WHERE User_id = %s", (user_id,))
            confirmed_reservations = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(Quantity) FROM Checkouts WHERE User_id = %s AND Return_date IS NULL", (user_id,))
            checked_out_books = cursor.fetchone()[0] or 0

            self.total_requested_books = confirmed_reservations + checked_out_books
            return self.total_requested_books
        except mysql.connector.Error as err:
            print(f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            db.close()


    def confirm_book(self):
        db = connect_to_mysql()
        cursor = db.cursor()
        cursor.execute("SELECT ID FROM Users WHERE Email = %s", (email_user,))
        user_id = cursor.fetchone()[0]

        try:
            cursor.execute("SELECT Reservation_id, Book_id, Quantity FROM Reservations WHERE User_id = %s AND Status = 'Chưa xác nhận'", (user_id,))
            reservation_data = cursor.fetchall()

            if not reservation_data:
                QMessageBox.information(self, "Thông báo", "Không có sách nào chưa xác nhận.")
                return
            
            reply = QMessageBox.question(
                self,
                "Xác nhận yêu cầu",
                "Bạn có thực sự muốn đặt trước tất cả số sách này?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.No:
                return
            
            for reservation in reservation_data:
                reservation_id, book_id, quantity = reservation

                if self.update_total_requested_books() > 10:
                    QMessageBox.warning(self, "Giới hạn yêu cầu sách", "Bạn đã đạt giới hạn yêu cầu sách (10 cuốn).")
                    return

                new_status = "Đã xác nhận"
                cursor.execute(
                    "UPDATE Reservations SET Status = %s, Reservation_date = DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 7 HOUR), Deadline = DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 175 HOUR) WHERE Reservation_id = %s",
                    (new_status, reservation_id),
                )
            db.commit()
                       

        except mysql.connector.Error as err:
            print(f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            self.refresh()

    def refresh(self):
        self.connection = connect_to_mysql()
        self.load_reserve()