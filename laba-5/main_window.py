import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Просмотрщик изображений")
        self.resize(800, 600)

        self.image_label = QLabel("Выберите файл аннотации, чтобы начать", self)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.open_button = QPushButton("Выбрать файл аннотации (.csv)", self)

        self.next_button = QPushButton("Следующее изображение", self)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.open_button)
        layout.addWidget(self.next_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
