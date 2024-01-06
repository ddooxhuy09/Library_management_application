from connect_to_mysql import connect_to_mysql

from PyQt6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.connection = connect_to_mysql()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Dashboard')

        layout = QVBoxLayout(self)
        
        total_books_layout = QHBoxLayout()
        available_books_layout = QVBoxLayout()
        borrowed_books_layout = QVBoxLayout()
        total_users_layout = QVBoxLayout()
        total_books_layout.addLayout(available_books_layout)
        total_books_layout.addLayout(borrowed_books_layout)
        total_books_layout.addLayout(total_users_layout)

        user_book_layout = QHBoxLayout()
        book_layout = QVBoxLayout()
        user_book_layout.addLayout(book_layout)
        user_layout = QVBoxLayout()
        user_book_layout.addLayout(user_layout)

        line_chart_layout = QVBoxLayout()

        layout.addLayout(total_books_layout)
        layout.addLayout(user_book_layout)
        layout.addLayout(line_chart_layout)

        self.display_total_available_books(available_books_layout)
        self.display_total_borrowed_books(borrowed_books_layout)
        self.display_total_users(total_users_layout)

        # Plot top books
        self.plot_top_books(book_layout)

        # Plot top users
        self.plot_top_users(user_layout)

        # Plot line chart for total books borrowed each month
        self.plot_line_chart(line_chart_layout)

        self.show()

    def display_total_available_books(self, layout):
        cursor = self.connection.cursor()

        query = "SELECT SUM(Quantity) FROM Books"
        cursor.execute(query)
        total_books = cursor.fetchone()[0]  # Fetch the result

        cursor.close()

        # Display the total number of books
        total_books_label = QLabel(f'Tổng sách hiện có: {total_books}')
        layout.addWidget(total_books_label)

    def display_total_borrowed_books(self, layout):
        cursor = self.connection.cursor()

        query = "SELECT SUM(Quantity) FROM Checkouts WHERE Return_date IS NULL "
        cursor.execute(query)
        total_books = cursor.fetchone()[0]  # Fetch the result

        cursor.close()

        # Display the total number of books
        total_books_label = QLabel(f'Tổng sách đang mượn: {total_books}')
        layout.addWidget(total_books_label)

    def display_total_users(self, layout):
        cursor = self.connection.cursor()

        query = "SELECT COUNT(*) FROM Users"
        cursor.execute(query)
        total_users = cursor.fetchone()[0]  # Fetch the result

        cursor.close()

        # Display the total number of books
        total_users_label = QLabel(f'Tổng số người dùng: {total_users}')
        layout.addWidget(total_users_label)

    def plot_top_books(self, layout):  # Pass the layout as an argument
        cursor = self.connection.cursor()

        query = """
            SELECT B.Name, SUM(C.Quantity) as S
            FROM Checkouts C
            JOIN Books B ON B.ID = C.Book_id
            GROUP BY C.Book_id
            ORDER BY S DESC
            LIMIT 10
        """
        cursor.execute(query)
        top_books = cursor.fetchall()
        cursor.close()

        # Tạo và hiển thị biểu đồ
        fig, ax = plt.subplots()
        books = [book[0] for book in top_books]
        borrow_counts = [book[1] for book in top_books]
        ax.bar(books, borrow_counts, color='green')  
        ax.set_ylabel('Số Lượt Mượn')
        ax.set_title('Top 10 Sách Được Mượn Nhiều Nhất')

        # Tạo FigureCanvas để hiển thị biểu đồ trong PyQt6
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)  # Use the provided layout

    def plot_top_users(self, layout):  # Pass the layout as an argument
        cursor = self.connection.cursor()

        query = """
            SELECT CONCAT(U.First_name, ' ', U.Last_name), SUM(C.Quantity) as S
            FROM Checkouts C
            JOIN Users U ON U.ID = C.User_id
            GROUP BY C.User_id
            ORDER BY S DESC
            LIMIT 10
        """
        cursor.execute(query)
        top_users = cursor.fetchall()
        cursor.close()

        # Tạo và hiển thị biểu đồ
        fig, ax = plt.subplots()
        users = [user[0] for user in top_users]
        borrow_counts = [user[1] for user in top_users]
        ax.bar(users, borrow_counts, color='yellow')  
        ax.set_ylabel('Số Lượt Mượn')
        ax.set_title('Top 10 người mượn nhiều sách nhất')

        # Tạo FigureCanvas để hiển thị biểu đồ trong PyQt6
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)  # Use the provided layout

    def plot_line_chart(self, layout):
        cursor = self.connection.cursor()

        query = """
            SELECT DATE_FORMAT(C.Checkout_date, '%Y-%m') AS Month, SUM(C.Quantity) as Total
            FROM Checkouts C
            GROUP BY Month
            ORDER BY Month
        """
        cursor.execute(query)
        monthly_data = cursor.fetchall()
        cursor.close()

        # Convert data to datetime objects for proper sorting
        months = [datetime.strptime(month[0], "%Y-%m") for month in monthly_data]
        total_borrowed = [month[1] for month in monthly_data]

        # Tạo và hiển thị biểu đồ đường
        fig, ax = plt.subplots()
        ax.plot(months, total_borrowed, marker='o', linestyle='-', color='blue')
        ax.set_ylabel('Tổng Số Sách Được Mượn')
        ax.set_xlabel('Tháng')
        ax.set_title('Tổng Số Sách Được Mượn Theo Tháng')

        # Tạo FigureCanvas để hiển thị biểu đồ trong PyQt6
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)