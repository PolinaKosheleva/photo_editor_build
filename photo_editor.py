"""
Простой фоторедактор (вариант 1: базовый фоторедактор).
Возможности: загрузка изображения, фильтр «Оттенки серого», сохранение.
"""

import os
import sys

import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QLabel, QMainWindow,
    QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

from filters import apply_grayscale


class PhotoEditor(QMainWindow):
    """Фоторедактор."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Фоторедактор")
        self.setGeometry(100, 100, 800, 600)

        self.current_image = None    # исходное изображение (BGR)
        self.processed_image = None  # результат обработки (BGR)

        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        self.image_label = QLabel("Загрузите изображение")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(700, 450)

        self.load_button = QPushButton("Загрузить")
        self.filter_button = QPushButton("Оттенки серого")
        self.save_button = QPushButton("Сохранить")

        self.load_button.clicked.connect(self.load_image)
        self.filter_button.clicked.connect(self.apply_filter)
        self.save_button.clicked.connect(self.save_image)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.load_button)
        layout.addWidget(self.filter_button)
        layout.addWidget(self.save_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_image(self):
        """Загрузка изображения через QFileDialog и cv2.imread()."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "",
            "Изображения (*.jpg *.jpeg *.png *.bmp)"
        )
        if not file_path:
            return  # пользователь закрыл диалог

        # cv2.imread не читает пути с кириллицей на Windows,
        # поэтому читаем файл как байты и декодируем
        try:
            data = np.fromfile(file_path, dtype=np.uint8)
            image = cv2.imdecode(data, cv2.IMREAD_COLOR)
        except OSError as e:
            self.show_error(f"Не удалось открыть файл:\n{e}")
            return

        if image is None:
            self.show_error("Файл повреждён или имеет неподдерживаемый формат.")
            return

        self.current_image = image
        self.processed_image = None
        self.display_image(image)

    def display_image(self, image):
        """Отображение изображения (BGR -> RGB -> QImage -> QPixmap)."""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, _ = rgb_image.shape
        bytes_per_line = 3 * w

        qimage = QImage(
            rgb_image.data, w, h, bytes_per_line,
            QImage.Format.Format_RGB888
        )
        pixmap = QPixmap.fromImage(qimage.copy())
        self.image_label.setPixmap(
            pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def apply_filter(self):
        """Применение фильтра «Оттенки серого»."""
        if self.current_image is None:
            self.show_error("Сначала загрузите изображение.")
            return

        result = apply_grayscale(self.current_image)
        self.processed_image = result.copy()  # сохраняем копию результата
        self.display_image(result)

    def save_image(self):
        """Сохранение обработанного изображения."""
        image_to_save = (
            self.processed_image
            if self.processed_image is not None
            else self.current_image
        )
        if image_to_save is None:
            self.show_error("Нет изображения для сохранения.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить изображение", "",
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)"
        )
        if not file_path:
            return

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in (".png", ".jpg", ".jpeg", ".bmp"):
            file_path += ".png"
            ext = ".png"

        # cv2.imencode + tofile работает и с кириллицей в пути
        ok, buffer = cv2.imencode(ext, image_to_save)
        if not ok:
            self.show_error("Не удалось закодировать изображение.")
            return
        try:
            buffer.tofile(file_path)
        except OSError as e:
            self.show_error(f"Не удалось сохранить файл:\n{e}")
            return

        QMessageBox.information(self, "Готово", f"Сохранено:\n{file_path}")

    def show_error(self, text):
        """Показать окно с ошибкой."""
        QMessageBox.warning(self, "Ошибка", text)


def main():
    app = QApplication(sys.argv)
    window = PhotoEditor()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
