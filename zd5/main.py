import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from task5 import Ui_Form


def resource_path(relative_path):
    """Возвращает путь к ресурсу (работает и в .py, и в .exe)."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class UfoApp(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Управление НЛО")
        self.resize(700, 500)
        
        pixmap = QPixmap(resource_path("ufo.png"))
        self.ufo.setPixmap(pixmap)
        self.ufo.setFixedSize(pixmap.size())
        self.ufo.move(300, 200)
        
        # Разрешаем обработку клавиш
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Шаг перемещения
        self.STEP = 20
    
    def keyPressEvent(self, event):
        """Обрабатывает нажатие клавиш-стрелок."""
        x = self.ufo.x()
        y = self.ufo.y()
        
        if event.key() == Qt.Key_Left:
            x -= self.STEP
        elif event.key() == Qt.Key_Right:
            x += self.STEP
        elif event.key() == Qt.Key_Up:
            y -= self.STEP
        elif event.key() == Qt.Key_Down:
            y += self.STEP
        else:
            super().keyPressEvent(event)
            return
        
        x = x % self.width()
        y = y % self.height()
        
        self.ufo.move(x, y)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UfoApp()
    window.show()
    sys.exit(app.exec_())