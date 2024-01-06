import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import QFile, QTextStream, QIODevice
from registration_page import RegistrationPage
from login_page import LoginPage
from forgot_password_page import ForgotPasswordPage
from confirmation_page import ConfirmationPage
from new_password_page import NewPasswordPage
from PyQt6.QtGui import QIcon


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("LibraryApp")
        self.setWindowTitle("Quản lý thư viện")
        self.setWindowIcon(QIcon("img/library.png"))
        self.setFixedSize(1000, 600)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.registration_page = RegistrationPage(self)
        self.login_page = LoginPage(self)
        self.forgot_password_page = ForgotPasswordPage(self)
        self.confirmation_page = None
        self.new_password_page = None
        
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.registration_page)
        self.stacked_widget.addWidget(self.forgot_password_page)
        
        self.show_page(0)
    
    def show_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
    
    def show_registration_page(self):
        self.show_page(1)
    
    def show_login_page(self):
        self.show_page(0)
    
    def show_forgot_password_page(self):
        self.show_page(2)
    
    def show_confirmation_page(self, email, confirmation_code):
        self.confirmation_page = ConfirmationPage(self, email, confirmation_code)
        self.stacked_widget.addWidget(self.confirmation_page)
        self.show_page(3)  
    
    def show_new_password_page(self, email):
        self.new_password_page = NewPasswordPage(self, email)
        self.stacked_widget.addWidget(self.new_password_page)
        self.show_page(4)

def main():
    app = QApplication(sys.argv)
    main_app = MainApp()
    css_file = QFile("css/login.css")
    if css_file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
        stream = QTextStream(css_file)
        app.setStyleSheet(stream.readAll())
        css_file.close()
    main_app.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()