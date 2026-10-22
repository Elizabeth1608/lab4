import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import Qt, QPoint
from task3 import Ui_Form


class DrawApp(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Рисование фигур")
        self.resize(800, 600)
        
        # Список нарисованных фигур
        # Каждая фигура: (тип, x, y, размер, цвет)
        self.shapes = []
        
        # Разрешаем обработку клавиш
        self.setFocusPolicy(Qt.StrongFocus)
    
    def mousePressEvent(self, event):
        """Обрабатывает нажатие кнопок мыши."""
        x = event.x()
        y = event.y()
        size = random.randint(30, 100)
        color = QColor(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        
        if event.button() == Qt.LeftButton:
            # Левая кнопка -> круг
            self.shapes.append(("circle", x, y, size, color))
            self.update()
        
        elif event.button() == Qt.RightButton:
            # Правая кнопка -> квадрат
            self.shapes.append(("square", x, y, size, color))
            self.update()
    
    def keyPressEvent(self, event):
        """Обрабатывает нажатие клавиш."""
        if event.key() == Qt.Key_Space:
            # Пробел → треугольник в позиции курсора
            pos = self.mapFromGlobal(self.cursor().pos())
            x = pos.x()
            y = pos.y()
            size = random.randint(30, 100)
            color = QColor(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            self.shapes.append(("triangle", x, y, size, color))
            self.update()
    
    def paintEvent(self, event):
        """Рисует все фигуры."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        for shape in self.shapes:
            kind, x, y, size, color = shape
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            
            if kind == "circle":
                # Круг
                painter.drawEllipse(x - size // 2, y - size // 2, size, size)
            
            elif kind == "square":
                # Квадрат
                painter.drawRect(x - size // 2, y - size // 2, size, size)
            
            elif kind == "triangle":
                # Треугольник (3 вершины)
                from PyQt5.QtGui import QPolygon
                from PyQt5.QtCore import QPoint
                p1 = QPoint(x, y - size // 2)              # верх
                p2 = QPoint(x - size // 2, y + size // 2)  # левый низ
                p3 = QPoint(x + size // 2, y + size // 2)  # правый низ
                painter.drawPolygon(QPolygon([p1, p2, p3]))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DrawApp()
    window.show()
    sys.exit(app.exec_())