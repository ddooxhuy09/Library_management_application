from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton
from database_utils import show_info_message
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class ConfirmationPage(QWidget):
    def __init__(self, parent, email, confirmation_code):
        super().__init__()
        self.parent = parent
        self.email = email
        self.confirmation_code = confirmation_code
        layout = QHBoxLayout()
        layout.setContentsMargins(5,0,0,0)
        form_layout = QVBoxLayout()
        self.confirmation_code_input = QLineEdit()
        
        form_layout.addWidget(QLabel(f"Nhập mã xác nhận đã gửi đến {self.email}"))
        form_layout.addWidget(self.confirmation_code_input)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        reset_button = QPushButton("Xác nhận")
        reset_button.clicked.connect(self.confirm)
        form_layout.addWidget(reset_button)
        layout.addLayout(form_layout)
        image_label = QLabel(self)
        pixmap = QPixmap("img/background.png")  # Change the path accordingly
        image_label.setPixmap(pixmap)
        image_label.setFixedSize(750, 600)
        layout.addWidget(image_label)
        # Set the main layout for the widget 
        self.setLayout(layout)
    
    def confirm(self):
        user_input = self.confirmation_code_input.text()
        if user_input == self.confirmation_code:
            self.parent.show_new_password_page(self.email)
        else:
            show_info_message("Nhập sai mã. Vui lòng nhập lại.")