from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
from email_utils import generate_confirmation_code, send_confirmation_email
from database_utils import is_email_exists, show_info_message
from PyQt6.QtGui import QPixmap

class ForgotPasswordPage(QWidget):
    def __init__(self, parent): 
        super().__init__()
        self.parent = parent

        layout = QHBoxLayout()
        layout.setContentsMargins(5,0,0,0) 
        # Create a form layout for the reset password form on the left
        form_layout = QVBoxLayout()
        self.email = QLineEdit()
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(QLabel("Nhập email:"))
        form_layout.addWidget(self.email)


        reset_button = QPushButton("Đặt lại mật khẩu")
        reset_button.clicked.connect(self.reset_password)
        form_layout.addWidget(reset_button)

        login_button = QPushButton("Nhớ mật khẩu. Đăng nhập")
        login_button.clicked.connect(self.parent.show_login_page)
        form_layout.addWidget(login_button)
        # Add the form layout to the left side
        layout.addLayout(form_layout)
        # Add the image to the right side
        image_label = QLabel(self)
        pixmap = QPixmap("img/background.png")  # Change the path accordingly
        image_label.setPixmap(pixmap)
        image_label.setContentsMargins(0, 0, 0, 0)
        image_label.setFixedSize(750, 600)
        layout.addWidget(image_label)

        # Set the main layout for the widget
        self.setLayout(layout)

    def reset_password(self):
        email = self.email.text()

        if not is_email_exists(email):
            show_info_message("Email không tồn tại.")
            return

        confirmation_code = generate_confirmation_code()
        send_confirmation_email(email, confirmation_code)

        self.parent.show_confirmation_page(email, confirmation_code)
