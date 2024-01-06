from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton
from database_utils import ( reset_password_in_database, show_info_message)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class NewPasswordPage(QWidget):
    def __init__(self, parent, email):
        super().__init__()
        self.parent = parent
        self.email = email
        
        layout = QHBoxLayout()
        layout.setContentsMargins(5,0,0,0)

        self.new_password_input = QLineEdit()
        self.confirm_password_input = QLineEdit()
        
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout= QVBoxLayout()
        form_layout.addWidget(QLabel(f"Nhập mật khẩu mới của {self.email}:"))
        form_layout.addWidget(self.new_password_input)
        form_layout.addWidget(QLabel("Nhập lại mật khẩu mới:"))
        form_layout.addWidget(self.confirm_password_input)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        reset_button = QPushButton("Đặt lại mật khẩu")
        reset_button.clicked.connect(self.reset_password)
        form_layout.addWidget(reset_button)
        layout.addLayout(form_layout)

        image_label = QLabel(self)
        pixmap = QPixmap("img/background.png")  # Change the path accordingly
        image_label.setPixmap(pixmap)
        image_label.setFixedSize(750, 600)
        layout.addWidget(image_label)
        # Set the main layout for the widget
        self.setLayout(layout)
    
    def reset_password(self):
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        if new_password != confirm_password:
            show_info_message("Mật khẩu không trùng khớp. Vui lòng nhập lại.")
            return
        
        reset_password_in_database(self.email, new_password)
        show_info_message("Đặt lại mật khẩu thành công.")
        self.parent.show_login_page() 
