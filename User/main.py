from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
    QFrame
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
import subprocess
import sys

from HomeWidget import HomeWidget
from ReserveListWidget import ReserveListWidget, set_email_user_ReserveListWidget
from UserInfoWindow import UserInfoWindow, set_email_user_UserInfoWindow
from HistoryWidget import HistoryWidget, set_email_user_HistoryWidget
from NotificationWidget import NotificationWidget, set_email_user_NotificationWidget
from BookInfoWindow import BookInfoWindow, set_email_user_BookInfoWindow, set_BookManagementApp

email_user = sys.argv[1]
set_email_user_ReserveListWidget(email_user)
set_email_user_UserInfoWindow(email_user)
set_email_user_HistoryWidget(email_user)
set_email_user_NotificationWidget(email_user)
set_email_user_BookInfoWindow(email_user)

class BookManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý thư viện")
        self.setFixedSize(1500, 800)
        self.setWindowIcon(QIcon("img/library.png"))

        logo_label = QLabel()
        logo_pixmap = QPixmap("img/LogoPTIT.png")
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.stacked_widget = QStackedWidget()
        self.home_widget = HomeWidget(self)
        self.reserve_list_Widget = ReserveListWidget(self)
        self.user_info_window = UserInfoWindow(self)
        self.history_widget = HistoryWidget(self)
        self.notification_widget = NotificationWidget(self, self.reserve_list_Widget)

        self.home_widget.setObjectName("home_widget_content")
        self.notification_widget.setObjectName("notification_widget_content")
        self.user_info_window.setObjectName("user_info_window_content")
        self.history_widget.setObjectName("history_widget_content")
        self.reserve_list_Widget.setObjectName("reserve_list_Widget_content")

        self.stacked_widget.addWidget(self.home_widget)
        self.stacked_widget.addWidget(self.notification_widget)
        self.stacked_widget.addWidget(self.user_info_window)
        self.stacked_widget.addWidget(self.history_widget)
        self.stacked_widget.addWidget(self.reserve_list_Widget)

        home_widget_icon = QIcon("img/home.png")
        notification_widget_icon = QIcon("img/notification.png")
        user_info_windowb_icon = QIcon("img/user.png")
        history_widget_icon = QIcon("img/checkout.png")
        reserve_list_widget_icon = QIcon("img/reservation.png")
        logout_icon = QIcon("img/logout.png")

        # Create buttons and connect them
        self.home_widget_button = self.create_button("Trang chủ", home_widget_icon,0, "home_widget_button")
        self.notification_widget_button = self.create_button("Thông báo",notification_widget_icon,1, "notification_widget_button")
        self.user_info_window_button = self.create_button("Người dùng",user_info_windowb_icon, 2, "user_info_window_button")
        self.history_widget_button = self.create_button("Lịch sử mượn",history_widget_icon, 3, "history_widget_button")
        self.reserve_list_widget_button = self.create_button("Đặt trước",reserve_list_widget_icon, 4, "reserve_list_widget_button")
        self.logout_button = self.create_button("Đăng xuất",logout_icon, 6, "logout_button")
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0,0,0,0) 
        
        button_layout.addWidget(self.home_widget_button)
        self.home_widget.book_info_requested.connect(self.show_book_info)
        button_layout.addWidget(self.notification_widget_button)
        button_layout.addWidget(self.user_info_window_button)
        button_layout.addWidget(self.history_widget_button)
        button_layout.addWidget(self.reserve_list_widget_button)
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

        self.home_widget_button.clicked.connect(self.change_button_state)
        self.notification_widget_button.clicked.connect(self.change_button_state)
        self.user_info_window_button.clicked.connect(self.change_button_state)
        self.history_widget_button.clicked.connect(self.change_button_state)
        self.reserve_list_widget_button.clicked.connect(self.change_button_state)
        self.logout_button.clicked.connect(self.show_logout)
        self.setStyleSheet(open("css/user.css", encoding="utf-8").read())

        tab_container = QFrame()
        tab_container.setContentsMargins(0, 0, 0, 0)
        tab_container.setObjectName("TabContainer")
        tab_container_layout = QVBoxLayout()
        tab_container_layout.setSpacing(0)

        tab_container_layout.addWidget(logo_label)
        tab_container_layout.addStretch(1)

        tab_container_layout.addWidget(self.home_widget_button)
        tab_container_layout.addWidget(self.notification_widget_button)
        tab_container_layout.addWidget(self.user_info_window_button)
        tab_container_layout.addWidget(self.history_widget_button)
        tab_container_layout.addWidget(self.reserve_list_widget_button)
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
    
    def show_book_info(self, Id, title, author, publisher, genre, description, image_path, quantity):
        book_info_window = BookInfoWindow(self, Id, title, author, publisher, genre, description, image_path, quantity, self.reserve_list_Widget, self.notification_widget)

        # Connect the quantity_updated signal to the update_quantity_label method
        self.reserve_list_Widget.quantity_updated.connect(book_info_window.update_quantity_label)

        self.stacked_widget.addWidget(book_info_window)
        self.stacked_widget.setCurrentWidget(book_info_window)

    def show_home(self):
        self.home_widget.clear_search()
        # Set the current index to 0
        self.stacked_widget.setCurrentIndex(0)

    def show_info(self):
        self.stacked_widget.setCurrentIndex(2)

    def show_notification(self):
        self.stacked_widget.setCurrentIndex(4)

    def show_reverse_list(self):
        self.stacked_widget.setCurrentIndex(1)

    def show_history(self):
        self.stacked_widget.setCurrentIndex(3)

    def show_logout(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText("Bạn có muốn đăng xuất?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        choice = msg.exec()
        if choice == QMessageBox.StandardButton.Yes:
            self.close() 
            subprocess.run(['python', 'Login/main.py'])

set_BookManagementApp(BookManagementApp)

if __name__ == "__main__":
    app = QApplication([])
    window = BookManagementApp()
    window.show()
    sys.exit(app.exec())