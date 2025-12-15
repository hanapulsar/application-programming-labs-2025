import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from iterator import ImageIterator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Просмотрщик изображений")
        self.resize(800, 600)

        self.iterator = None

        self.image_label = QLabel("Выберите файл аннотации, чтобы начать", self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.open_button = QPushButton("Выбрать файл аннотации (.csv)", self)
        self.next_button = QPushButton("Следующее изображение", self)
        self.next_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.open_button)
        layout.addWidget(self.next_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.open_button.clicked.connect(self.open_annotation_file)
        self.next_button.clicked.connect(self.show_next_image)

    def open_annotation_file(self):
        """Открывает диалог выбора файла и создает итератор."""
        filepath, _ = QFileDialog.getOpenFileName(self, "Выбрать файл аннотации", "", "CSV файлы (*.csv)")

        if filepath:
            try:
                self.iterator = ImageIterator(filepath)
                self.next_button.setEnabled(True)
                self.image_label.setText("Файл загружен. Нажмите 'Следующее изображение'.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить итератор: {e}")

    def show_next_image(self):
        """Загружает и отображает следующее изображение из итератора."""
        if self.iterator is None:
            return

        try:
            image_path = next(self.iterator)
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)

        except StopIteration:
            self.image_label.setText("Изображения закончились!")
            self.next_button.setEnabled(False)
            QMessageBox.information(self, "Завершено", "Вы просмотрели все изображения.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить изображение: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
