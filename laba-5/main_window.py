import sys
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, \
    QFileDialog, QMessageBox, QScrollArea

from iterator import ImageIterator


class MainWindow(QMainWindow):
    """
    Главное окно приложения для просмотра изображений из датасета.
    Позволяет выбирать файл аннотации, просматривать изображения
    последовательно и изменять их масштаб.
    """
    ZOOM_STEP = 1.25

    def __init__(self) -> None:
        """
        Инициализирует главное окно, создает виджеты и их компоновку.
        """
        super().__init__()

        self.setWindowTitle("Просмотрщик изображений")
        self.resize(800, 600)

        self.iterator: Optional[ImageIterator] = None
        self.current_pixmap: Optional[QPixmap] = None
        self.zoom_factor: float = 1.0

        self.image_label = QLabel("Выберите файл аннотации, чтобы начать", self)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setWidget(self.image_label)

        self.open_button = QPushButton("Выбрать файл аннотации (.csv)", self)
        self.next_button = QPushButton("Следующее изображение", self)
        self.zoom_in_button = QPushButton("Zoom In (+)", self)
        self.zoom_out_button = QPushButton("Zoom Out (-)", self)

        self.next_button.setEnabled(False)
        self.zoom_in_button.setEnabled(False)
        self.zoom_out_button.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.next_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.zoom_out_button)
        button_layout.addWidget(self.zoom_in_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.scroll_area, 1)
        main_layout.addLayout(button_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.open_button.clicked.connect(self.open_annotation_file)
        self.next_button.clicked.connect(self.show_next_image)
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)

    def open_annotation_file(self) -> None:
        """
        Открывает диалог выбора файла и создает итератор.
        """
        filepath, _ = QFileDialog.getOpenFileName(self, "Выбрать файл аннотации", "", "CSV файлы (*.csv)")

        if filepath:
            try:
                self.iterator = ImageIterator(filepath)
                self.next_button.setEnabled(True)
                self.current_pixmap = None
                self.update_image_display()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить итератор: {e}")

    def show_next_image(self) -> None:
        """
        Загружает и отображает следующее изображение из итератора.
        """
        if self.iterator is None:
            return

        try:
            image_path = next(self.iterator)
            self.current_pixmap = QPixmap(image_path)

            if self.current_pixmap.isNull():
                raise Exception("Не удалось загрузить изображение (возможно, файл поврежден).")

            img_w = self.current_pixmap.width()
            img_h = self.current_pixmap.height()

            area_w = self.scroll_area.viewport().width()
            area_h = self.scroll_area.viewport().height()

            if img_w > 0 and img_h > 0:
                w_ratio = area_w / img_w
                h_ratio = area_h / img_h

                self.zoom_factor = min(w_ratio, h_ratio)
            else:
                self.zoom_factor = 1.0

            self.zoom_in_button.setEnabled(True)
            self.zoom_out_button.setEnabled(True)

            self.update_image_display()

        except StopIteration:
            self.next_button.setEnabled(False)
            self.zoom_in_button.setEnabled(False)
            self.zoom_out_button.setEnabled(False)
            self.current_pixmap = None
            self.update_image_display()
            QMessageBox.information(self, "Завершено", "Вы просмотрели все изображения.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить изображение: {e}")

    def zoom_in(self) -> None:
        """
        Увеличивает масштаб изображения.
        """
        self.zoom_factor *= self.ZOOM_STEP
        self.update_image_display()

    def zoom_out(self) -> None:
        """
        Уменьшает масштаб изображения.
        """
        self.zoom_factor /= self.ZOOM_STEP
        self.update_image_display()

    def update_image_display(self) -> None:
        """
        Масштабирует и отображает текущее изображение.
        """
        if self.current_pixmap and not self.current_pixmap.isNull():
            new_size = self.current_pixmap.size() * self.zoom_factor
            scaled_pixmap = self.current_pixmap.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.resize(scaled_pixmap.size())
        else:
            self.image_label.clear()
            if self.iterator and self.next_button.isEnabled():
                self.image_label.setText("Файл загружен. Нажмите 'Следующее изображение'")
            elif self.iterator and not self.next_button.isEnabled():
                self.image_label.setText("Изображения закончились! Выберите новый файл.")
            self.image_label.adjustSize()


def main() -> None:
    """
    Инициализирует и запускает приложение.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
