import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox, QSizePolicy
from PyQt5.QtGui import QPixmap, QResizeEvent
from PyQt5.QtCore import Qt

from iterator import ImageIterator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Просмотрщик изображений")
        self.resize(800, 600)

        self.iterator = None
        self.current_pixmap = None

        self.zoom_factor = 1.0
        self.ZOOM_STEP = 1.25

        self.image_label = QLabel("", self)
        self.image_label.setAlignment(Qt.AlignCenter)
        size_policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.image_label.setSizePolicy(size_policy)

        self.open_button = QPushButton("Выбрать файл аннотации (.csv)", self)

        self.next_button = QPushButton("Следующее изображение", self)
        self.next_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label, 1)
        layout.addWidget(self.open_button)
        layout.addWidget(self.next_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.open_button.clicked.connect(self.open_annotation_file)
        self.next_button.clicked.connect(self.show_next_image)

    def open_annotation_file(self):
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

    def show_next_image(self):
        """
        Загружает и отображает следующее изображение из итератора.
        """
        if self.iterator is None:
            return

        try:
            image_path = next(self.iterator)
            self.current_pixmap = QPixmap(image_path)
            self.update_image_display()

        except StopIteration:
            self.next_button.setEnabled(False)
            self.current_pixmap = None
            self.update_image_display()
            QMessageBox.information(self, "Завершено", "Вы просмотрели все изображения.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить изображение: {e}")

    def update_image_display(self):
        """
        Масштабирует и отображает текущее изображение.
        """
        if self.current_pixmap and not self.current_pixmap.isNull():
            scaled_pixmap = self.current_pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.clear()
            if self.iterator and self.next_button.isEnabled():
                self.image_label.setText("Файл загружен. Нажмите 'Следующее изображение'")
            elif self.iterator and not self.next_button.isEnabled():
                self.image_label.setText("Изображения закончились! Выберите новый файл.")
            else:
                self.image_label.setText("Выберите файл аннотации, чтобы начать")

    def resizeEvent(self, event: QResizeEvent):
        """
        Этот метод автоматически вызывается при изменении размера окна.
        """
        self.update_image_display()
        super().resizeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
