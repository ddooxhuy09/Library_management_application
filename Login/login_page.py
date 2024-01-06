from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox
from PyQt6.QtGui import QPixmap
from database_utils import (login_user, show_info_message)
from PyQt6.QtCore import Qt
import subprocess

class LoginPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        layout = QHBoxLayout()
        layout.setContentsMargins(5,0,0,0)  
        # Create a form layout for the login form on the right
        form_layout = QVBoxLayout()
        self.email = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(QLabel("Tài khoản (Email):"))
        form_layout.addWidget(self.email)
        form_layout.addWidget(QLabel("Mật khẩu:"))
        form_layout.addWidget(self.password)

        self.show_password_checkbox = QCheckBox("Hiển thị mật khẩu")
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        form_layout.addWidget(self.show_password_checkbox)

        login_button = QPushButton("Đăng nhập")
        login_button.clicked.connect(self.login)
        form_layout.addWidget(login_button)

        register_button = QPushButton("Tôi không có tài khoản. Đăng ký")
        register_button.clicked.connect(self.parent.show_registration_page)
        form_layout.addWidget(register_button)

        forgot_password_button = QPushButton("Quên mật khẩu")
        forgot_password_button.clicked.connect(self.parent.show_forgot_password_page)
        form_layout.addWidget(forgot_password_button)

        # Set the form layout for the right side
        layout.addLayout(form_layout)
        image_label = QLabel(self)
        pixmap = QPixmap("img/background.png")  # Change the path accordingly
        image_label.setPixmap(pixmap)
        image_label.setFixedSize(750, 600)
        layout.addWidget(image_label)
        # Set the main layout for the widget
        self.setLayout(layout)

    def toggle_password_visibility(self):
        if self.show_password_checkbox.isChecked():
            # When the checkbox is checked, show the password
            self.password.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            # When the checkbox is unchecked, hide the password
            self.password.setEchoMode(QLineEdit.EchoMode.Password)

    def login(self):
        email = self.email.text()
        password = self.password.text()

        if email == "admin" and password == "1":

            show_info_message("Đăng nhập với chức năng admin thành công!")
            self.parent.close()
            subprocess.run(['python', 'Admin/main.py'])
                
        elif login_user(email, password):
            show_info_message("Đăng nhập thành công!")
            self.parent.close()
            subprocess.run(['python', 'User/main.py', email])
        else:
            show_info_message("Đăng nhập thất bại. Email hoặc mật khẩu không đúng")