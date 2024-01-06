from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel
)
from PyQt6.QtGui import QPixmap, QImage
import requests

class BookWidget(QWidget):
    def __init__(self, parent, title, image_path):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.image_label = QLabel(self)
        self.title_label = QLabel(title, self)
        layout.addWidget(self.image_label)
        layout.addWidget(self.title_label)
        self.setLayout(layout)
        self.set_image(image_path)

    def set_image(self, image_path):
        if image_path[0] == 'h':
            image = QImage()
            image.loadFromData(requests.get(image_path).content)
        else:
            image = image_path

        pixmap = QPixmap(image)
        self.image_label.setPixmap(pixmap.scaledToWidth(200))
