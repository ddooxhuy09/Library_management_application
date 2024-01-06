from PyQt6.QtWidgets import (QLabel,QVBoxLayout,QWidget)
from PyQt6.QtGui import QImage, QPixmap
import requests

class BookInfoWidget(QWidget):
    def __init__(self, title, genre, author, publisher, description, quantity, image_path):
        super().__init__()

        layout = QVBoxLayout()

        self.title_label = QLabel(f"Tên Sách: {title}")
        layout.addWidget(self.title_label)

        self.genre_label = QLabel(f"Thể Loại: {genre}")
        layout.addWidget(self.genre_label)

        self.author_label = QLabel(f"Tác Giả: {author}")
        layout.addWidget(self.author_label)

        self.publisher_label = QLabel(f"Thể Loại: {publisher}")
        layout.addWidget(self.publisher_label)

        self.description_label = QLabel(f"Mô Tả Sách: {description}")
        layout.addWidget(self.description_label)

        self.quantity_label = QLabel(f"Số Lượng: {quantity}")
        layout.addWidget(self.quantity_label)

        if image_path[0] == 'h':
            image = QImage()
            image.loadFromData(requests.get(image_path).content)
        else:
            image = image_path

        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap(image))
        self.image_label.setScaledContents(True)
        layout.addWidget(self.image_label)

        self.setLayout(layout)