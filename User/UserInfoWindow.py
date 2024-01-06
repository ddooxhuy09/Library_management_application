from connect_to_mysql import connect_to_mysql
import mysql.connector
import re
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QPushButton,
    QLabel,
    QStackedWidget,
    QLineEdit,
    QCheckBox,
    QFormLayout
)
from PyQt6.QtCore import Qt

def set_email_user_UserInfoWindow(email):
    global email_user
    email_user = email

class UserInfoWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thông tin người dùng")

        self.initUI()
        self.load_user_data()  # Load user data when the window is created

        # Store the passwords
        self.current_password = ""
        self.new_password = ""
        self.confirm_password = ""

    def initUI(self):
        self.stacked_widget = QStackedWidget()

        # Create and add the info page
        info_page = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(5, 0, 5, 0)

        self.reader_id_value = QLabel()
        layout.addWidget(self.reader_id_value)
        
        self.fname_value = QLabel()
        layout.addWidget(self.fname_value)

        self.lname_value = QLabel()
        layout.addWidget(self.lname_value)
        self.edit_name_button = QPushButton("Chỉnh sửa")
        self.edit_name_button.clicked.connect(self.edit_name_clicked)
        layout.addWidget(self.edit_name_button)


        self.email_value = QLabel()
        layout.addWidget(self.email_value)

        self.password_value = QLabel()
        layout.addWidget(self.password_value)

        self.edit_password_button = QPushButton("Chỉnh sửa")
        self.edit_password_button.clicked.connect(self.edit_password_clicked)
        layout.addWidget(self.edit_password_button)

        # Inside the __init__ method, after setting up other labels
        self.usage_time_value = QLabel()
        layout.addWidget(self.usage_time_value)

        info_page.setLayout(layout)
        self.stacked_widget.addWidget(info_page)

        # Create and add the name edit page
        name_edit_page = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(5, 0, 5, 0)
        form_layout = QFormLayout()
        self.fname_label_edit = QLabel("Họ:")
        self.fname_edit = QLineEdit()
        form_layout.addRow(self.fname_label_edit, self.fname_edit)

        self.lname_label_edit = QLabel("Tên:")
        self.lname_edit = QLineEdit()
        # layout.addWidget(self.lname_label_edit)
        # layout.addWidget(self.lname_edit)
        form_layout.addRow(self.lname_label_edit, self.lname_edit)

        self.save_name_button = QPushButton("Lưu")
        self.save_name_button.clicked.connect(self.save_name_clicked)
        
        self.cancel_name_button = QPushButton("Hủy")
        self.cancel_name_button.clicked.connect(self.cancel_name_clicked)
        layout.addLayout(form_layout)
        layout.addWidget(self.save_name_button)
        layout.addWidget(self.cancel_name_button)
        name_edit_page.setLayout(layout)
        self.stacked_widget.addWidget(name_edit_page)

        # Create and add the password edit page
        password_edit_page = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(5, 0, 5, 0)
        self.old_password_label = QLabel("Mật khẩu cũ:")
        self.old_password_edit = QLineEdit()
        self.old_password_edit.setEchoMode(QLineEdit.EchoMode.Password)  # Set the echo mode to hide the password
        layout.addWidget(self.old_password_label)
        layout.addWidget(self.old_password_edit)

        self.new_password_label = QLabel("Mật khẩu mới:")
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)  # Set the echo mode to hide the password
        layout.addWidget(self.new_password_label)
        layout.addWidget(self.new_password_edit)

        self.confirm_password_label = QLabel("Nhập lại mật khẩu mới:")
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)  # Set the echo mode to hide the password
        layout.addWidget(self.confirm_password_label)
        layout.addWidget(self.confirm_password_edit)

        # Create a label widget for displaying password instructions
        self.password_instruction_label = QLabel()
        layout.addWidget(self.password_instruction_label)

        self.show_password_checkbox = QCheckBox("Hiển thị mật khẩu")
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_checkbox)

        self.save_password_button = QPushButton("Lưu")
        self.save_password_button.clicked.connect(self.save_password_clicked)
        layout.addWidget(self.save_password_button)

        self.cancel_password_button = QPushButton("Hủy")
        self.cancel_password_button.clicked.connect(self.cancel_password_clicked)
        layout.addWidget(self.cancel_password_button)

        password_edit_page.setLayout(layout)
        self.stacked_widget.addWidget(password_edit_page)

        self.setCentralWidget(self.stacked_widget)

    def toggle_password_visibility(self):
        if self.show_password_checkbox.isChecked():
            # When the checkbox is checked, show the password
            self.old_password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            # When the checkbox is unchecked, hide the password
            self.old_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def load_user_data(self):
        db = connect_to_mysql()

        if db is None:
            return  # Handle the error appropriately

        try:
            cursor = db.cursor()

            # Fetch user data
            cursor.execute(
                "SELECT ID, First_name, Last_name, Email, Password FROM Users WHERE Email = %s",
                (email_user,),
            )
            user_data = cursor.fetchone()

            if user_data:
                user_id, first_name, last_name, email, password = user_data
                self.reader_id_value.setText(f"Mã người đọc:  {str(user_id)}")  # Display the user ID
                self.fname_value.setText(f"Họ: {first_name}")
                self.lname_value.setText(f"Tên: {last_name}")
                self.email_value.setText(f"Email: {email}")
                self.password_value.setText("Mật khẩu: ******")  # You should not display the actual password

                # Fetch Usage_time separately
                cursor.execute(
                    "SELECT Status FROM Expiry WHERE ID = %s",
                    (user_id,)
                )
                expiry_data = cursor.fetchone()

                if expiry_data:
                    usage_time = expiry_data[0]
                    self.usage_time_value.setText(f"Thời gian mượn sách của bạn: {usage_time}")
                else:
                    self.usage_time_value.setText("Thời gian mượn sách của bạn: Bạn chưa đăng kí thẻ mượn")

            cursor.close()

        except mysql.connector.Error as e:
            print("Error:", e)

        finally:
            db.close()

    def edit_name_clicked(self):
        self.stacked_widget.setCurrentIndex(1)  # Switch to the name edit page

    def save_name_clicked(self):
        new_fname = self.fname_edit.text()
        new_lname = self.lname_edit.text()

        if not new_fname or not new_lname:
            QMessageBox.critical(self, "Trống thông tin", "Họ và tên không được để trống.")
            return

        db = connect_to_mysql()
        if db is None:
            return  # Handle the error appropriately

        try:
            cursor = db.cursor()

            # Check if the new name is the same as the current name
            cursor.execute("SELECT First_name, Last_name FROM Users WHERE Email = %s", (email_user,))
            current_name = cursor.fetchone()
            
            if current_name and current_name == (new_fname, new_lname):
                QMessageBox.critical(self, "Trùng tên", "Họ tên mới trùng với họ tên hiện tại.")
            else:
                # Update the name in the database
                cursor.execute("UPDATE Users SET First_name = %s, Last_name = %s WHERE Email = %s", (new_fname, new_lname, email_user))
                db.commit()
                self.fname_value.setText(f"Họ: {new_fname}")
                self.lname_value.setText(f"Tên: {new_lname}")
                QMessageBox.information(self, "Thành công", "Đổi họ tên thành công")
                # Restore the info page

        except mysql.connector.Error as e:
            print("Error:", e)
        finally:
            db.close()


        # Clear the name fields
        self.fname_edit.clear()
        self.lname_edit.clear()
        self.stacked_widget.setCurrentIndex(0)   

    def cancel_name_clicked(self):
        # Check if the name fields are not empty before asking for confirmation
        if self.fname_edit.text() or self.lname_edit.text():
            reply = QMessageBox.question(
                self,
                "Xác nhận hủy",
                "Bạn thực sự muốn hủy?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # Restore the info page
        self.stacked_widget.setCurrentIndex(0)
        self.fname_edit.clear()
        self.lname_edit.clear()

    def edit_password_clicked(self):
        self.stacked_widget.setCurrentIndex(2)  # Switch to the password edit page

    def save_password_clicked(self):
        old_password = self.old_password_edit.text()
        new_password = self.new_password_edit.text()
        confirm_password = self.confirm_password_edit.text()

        self.current_password = old_password
        self.new_password = new_password
        self.confirm_password = confirm_password

        # Check if the old password matches the current password
        db = connect_to_mysql()
        if db is None:
            return  # Handle the error appropriately

        try:
            cursor = db.cursor()

            cursor.execute("SELECT Password FROM Users WHERE Email = %s", (email_user,))
            current_password = cursor.fetchone()[0]

            if not old_password or not new_password or not confirm_password:
                self.show_password_instruction("Trống thông tin", "Không được để trống các ô mật khẩu.")
              
            if old_password != current_password:
                self.show_password_instruction("Mật khẩu cũ không chính xác.")
            # Check if the new password matches the current password
            elif new_password == current_password:
                self.show_password_instruction("Mật khẩu mới không được trùng với mật khẩu hiện tại.")
            # Check if the new password and confirm password match
            elif new_password != confirm_password:
                self.show_password_instruction("Xác nhận mật khẩu không trùng khớp.")
            # Check if the new password meets the requirements
            elif not self.is_valid_password(new_password):
                self.show_password_instruction("Mật khẩu phải có ít nhất 8 ký tự bao gồm chữ hoa, chữ thường, chữ số và ký tự đặc biệt")
            else:
                # Update the password in the database
                cursor.execute("UPDATE Users SET Password = %s WHERE Email = %s", (new_password, email_user))
                QMessageBox.information(self, "Thành công", "Đổi mật khẩu thành công")
                # Restore the info page
                self.stacked_widget.setCurrentIndex(0)
                db.commit()
                # Clear the password fields
            self.old_password_edit.clear()
            self.new_password_edit.clear()
            self.confirm_password_edit.clear()  
            
        except mysql.connector.Error as e:
            print("Error:", e)
        finally:
            db.close()

    def show_password_instruction(self, message, is_error=True):
        self.password_instruction_label.setText(message)
        if is_error:
            self.password_instruction_label.setStyleSheet("color: red;")

    def is_valid_password(self, password):
        # Use a regular expression to check if the password meets the requirements
        # At least 8 characters, including at least one uppercase letter, one lowercase letter, one digit, and one special character
        pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&+=]).{8,}$"
        return re.match(pattern, password) is not None

    def cancel_password_clicked(self):
        # Check if the password fields are not empty before asking for confirmation
        if (
            self.old_password_edit.text()
            or self.new_password_edit.text()
            or self.confirm_password_edit.text()
        ):
            reply = QMessageBox.question(
                self,
                "Xác nhận hủy",
                "Bạn thực sự muốn hủy?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
            
        self.old_password_edit.clear()
        self.new_password_edit.clear()
        self.confirm_password_edit.clear()      
        self.stacked_widget.setCurrentIndex(0)