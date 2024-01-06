from ListBooksApp import ListBooksApp
from AddBookApp import AddBookApp
from ListUsersApp import ListUsersApp
from ExpiryWidget import ExpiryWidget
from ListCheckouts import ListCheckouts
from ListReservations import ListReservations
from DashboardWidget import DashboardWidget

import sys
import subprocess
from PyQt6.QtCore import Qt,QPoint
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QStackedWidget,
    QFrame,
)

from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtGui import QPixmap, QIcon


class LibraryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("LibraryApp")
        self.setWindowTitle("Quản lý thư viện")
        self.setFixedSize(1500, 800)
        self.setWindowIcon(QIcon("img/library.png"))
        logo_label = QLabel()
        logo_pixmap = QPixmap("img/LogoPTIT.png")
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drag_position = QPoint()
        self.stacked_widget = QStackedWidget()
        list_books_app = ListBooksApp()
        self.list_books_tab = list_books_app
        self.add_book_tab = AddBookApp(list_books_app)
        self.list_users_tab = ListUsersApp()
        self.expiry_tab = ExpiryWidget()       
        self.list_checkouts_tab = ListCheckouts()
        self.list_reservations_tab = ListReservations()
        self.dashboard_tab = DashboardWidget()
        
        self.list_books_tab.setObjectName("list_books_content")
        self.add_book_tab.setObjectName("add_book_content")
        self.expiry_tab.setObjectName("expiry_content")
        self.dashboard_tab.setObjectName("dashboard_content")
        self.logout_widget = QWidget()

        self.stacked_widget.addWidget(self.list_books_tab)
        self.stacked_widget.addWidget(self.add_book_tab)
        self.stacked_widget.addWidget(self.list_users_tab)
        self.stacked_widget.addWidget(self.expiry_tab)
        self.stacked_widget.addWidget(self.list_checkouts_tab)
        self.stacked_widget.addWidget(self.list_reservations_tab)
        self.stacked_widget.addWidget(self.dashboard_tab)
        self.stacked_widget.addWidget(self.logout_widget)

        add_tab_icon = QIcon("img/add.png")
        list_tab_icon = QIcon("img/list.png")
        expiry_tab_icon = QIcon("img/expiry.png")
        user_tab_icon = QIcon("img/user.png")
        checkouts_tab_icon = QIcon("img/checkout.png")
        reservations_icon = QIcon("img/reservation.png")
        dashboard_icon = QIcon("img/dashboard.png")
        logout_icon = QIcon("img/logout.png")

        self.list_books_button = self.create_button("Danh sách sách", list_tab_icon, 0, "list_books_button")
        self.add_book_button = self.create_button("Thêm sách", add_tab_icon, 1, "add_book_button")
        self.list_users_button = self.create_button("Người dùng", user_tab_icon, 2, "list_users_button")
        self.expiry_button = self.create_button("Thời gian dùng thẻ", expiry_tab_icon, 3, "expiry_button")
        self.list_checkouts_button = self.create_button("Lịch sử mượn sách", checkouts_tab_icon, 4, "list_checkouts_button")
        self.list_reservations_button = self.create_button("Danh sách đặt sách", reservations_icon, 5, "list_reservations_button")
        self.dashboard_button = self.create_button("Biểu đồ báo cáo", dashboard_icon, 6, "dashboard_button")
        self.logout_button = self.create_button("Đăng xuất", logout_icon, 7, "logout_button")
        
        button_layout = QVBoxLayout()
        button_layout.setSpacing(0)
        button_layout.setContentsMargins(0,0,0,0) 
        
        button_layout.addWidget(self.list_books_button)
        button_layout.addWidget(self.add_book_button)
        button_layout.addWidget(self.list_users_button)
        button_layout.addWidget(self.expiry_button)
        button_layout.addWidget(self.list_checkouts_button)
        button_layout.addWidget(self.list_reservations_button)
        button_layout.addWidget(self.dashboard_button)
        button_layout.addWidget(self.logout_button)
        button_widget = QWidget()
        button_widget.setLayout(button_layout)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0,0,0,0) 
        main_layout.setSpacing(0)

        main_layout.addWidget(button_widget)
        main_layout.addWidget(self.stacked_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.current_button = None

        self.list_books_button.clicked.connect(self.change_button_state)
        self.add_book_button.clicked.connect(self.change_button_state)
        self.list_users_button.clicked.connect(self.change_button_state)
        self.expiry_button.clicked.connect(self.change_button_state)    
        self.list_checkouts_button.clicked.connect(self.change_button_state)
        self.list_reservations_button.clicked.connect(self.change_button_state)
        self.dashboard_button.clicked.connect(self.change_button_state)
        self.logout_button.clicked.connect(self.show_logout)

        self.setStyleSheet(open("css/admin.css", encoding="utf-8").read())
        tab_container = QFrame()

        tab_container.setContentsMargins(0, 0, 0, 0)
        tab_container.setObjectName("TabContainer")
        tab_container_layout = QVBoxLayout()
        tab_container_layout.setSpacing(0)
        tab_container_layout.addWidget(logo_label)
        tab_container_layout.addStretch(1)
        tab_container_layout.addWidget(self.list_books_button)
        tab_container_layout.addWidget(self.add_book_button)
        tab_container_layout.addWidget(self.list_users_button)
        tab_container_layout.addWidget(self.expiry_button)
        tab_container_layout.addWidget(self.list_checkouts_button)
        tab_container_layout.addWidget(self.list_reservations_button)
        tab_container_layout.addWidget(self.dashboard_button)
        tab_container_layout.setContentsMargins(0, 0, 0, 0)

        tab_container_layout.addStretch(1)
        tab_container_layout.addWidget(self.logout_button)
        tab_container.setLayout(tab_container_layout)

        main_layout.addWidget(tab_container)
        main_layout.addWidget(self.stacked_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.current_button = None
    
    def create_button(self, text, icon, index, button_class):
        button = QPushButton(text)
        button.setIcon(icon)
        button.setObjectName(button_class)
        button.setCheckable(True)
        button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(index))

        button.setFixedSize(200, 60)
        return button
    
    def change_button_state(self):
        sender = self.sender()
        if sender == self.current_button:
            return
        if self.current_button:
            self.current_button.setChecked(False)
        self.current_button = sender
        self.current_button.setChecked(True)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition()

    def mouseMoveEvent(self, event):
        if not self.drag_position.isNull():
            delta = event.globalPosition() - self.drag_position
            new_x = self.x() + delta.x()
            new_y = self.y() + delta.y()
            self.move(int(new_x), int(new_y))
            self.drag_position = event.globalPosition()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = QPoint()

    def show_logout(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText("Bạn có muốn đăng xuất?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        choice = msg.exec()
        if choice == QMessageBox.StandardButton.Yes:
            self.close() 
            subprocess.run(['python', 'Login/main.py'])

def main():
    app = QApplication(sys.argv)    
    window = LibraryApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()