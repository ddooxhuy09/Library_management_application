from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from database_utils import (is_valid_password, register_user,show_info_message)
import re

class RegistrationPage(QWidget):
    registration_successful = pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
    
        layout = QHBoxLayout()      
        layout.setContentsMargins(5,0,0,0) 
        form_layout = QVBoxLayout()
        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        form_layout.addWidget(QLabel("Họ:"))
        form_layout.addWidget(self.first_name)
        form_layout.addWidget(QLabel("Tên:"))
        form_layout.addWidget(self.last_name)

        # Add the email, password, and user type fields to the form layout
        self.email = QLineEdit()
        self.password = QLineEdit()
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Nhập lại mật khẩu")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(QLabel("Email:"))
        form_layout.addWidget(self.email)
        form_layout.addWidget(QLabel("Mật khẩu:"))
        form_layout.addWidget(self.password)
        form_layout.addWidget(QLabel("Nhập lại mật khẩu:"))
        form_layout.addWidget(self.confirm_password)

        self.user_type_combo = QComboBox()
        self.user_type_combo.addItem("Sinh viên")
        self.user_type_combo.addItem("Giáo viên")
        self.user_type_combo.addItem("Khác")
        form_layout.addWidget(QLabel("Đối tượng:"))
        form_layout.addWidget(self.user_type_combo)

        # Add the register button to the form layout
        register_button = QPushButton("Đăng ký")
        register_button.clicked.connect(self.register)
        form_layout.addWidget(register_button)
        # Add the login button to the right side
        login_button = QPushButton("Đăng nhập")
        login_button.clicked.connect(self.parent.show_login_page)
        form_layout.addWidget(login_button)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Set the form layout for the right side
        layout.addLayout(form_layout)
        image_label = QLabel(self)
        pixmap = QPixmap("img/background.png")  # Change the path accordingly
        image_label.setPixmap(pixmap)
        image_label.setContentsMargins(0,0,0,0)
        image_label.setFixedSize(750, 600)
        layout.addWidget(image_label)
        # Set the main layout for the widget

        self.setLayout(layout)

    def register(self):
        first_name = self.first_name.text()
        last_name = self.last_name.text()
        email = self.email.text()
        password = self.password.text()
        confirm_password = self.confirm_password.text()

        email_validate_pattern = r"^\S+@\S+\.\S+$"     

        if not re.match(email_validate_pattern, email):
            show_info_message("Email không đúng cú pháp.")
            return
    
        if not is_valid_password(password):
            show_info_message("Mật khẩu phải có ít nhất 8 ký tự gồm chữ HOA, chữ thường, chữ số và ký tự đặc biệt.")
            return
        
        if password != confirm_password:
            show_info_message("Mật khẩu và nhập lại mật khẩu không trùng khớp.")
            return

        user_type = self.user_type_combo.currentText()

        if register_user(first_name, last_name, email, password, user_type):
            show_info_message("Đăng ký thành công!")
            self.registration_successful.emit()
            
            self.first_name.clear()
            self.last_name.clear()
            self.email.clear()
            self.password.clear()
            self.confirm_password.clear()

        else:
            show_info_message("Đăng ký thất bại. Email đã tồn tại hoặc có lỗi xảy ra.")