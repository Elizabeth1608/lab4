import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt
from task4 import Ui_Form


class RunawayButton(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Убегающая кнопка")
        self.resize(700, 500)
        
        # Включаем отслеживание мыши без нажатия
        self.setMouseTracking(True)
        
        # Радиус "страха" — на каком расстоянии кнопка убегает
        self.danger_radius = 150
    
    def mouseMoveEvent(self, event):
        """Двигаем кнопку, когда курсор близко."""
        # Позиция курсора на форме
        mx = event.x()
        my = event.y()
        
        # Центр кнопки
        btn_center_x = self.btn.x() + self.btn.width() / 2
        btn_center_y = self.btn.y() + self.btn.height() / 2
        
        # Расстояние от курсора до центра кнопки
        dx = mx - btn_center_x
        dy = my - btn_center_y
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance < self.danger_radius:
            self.move_button_away(mx, my)
    
    def move_button_away(self, mx, my):
        """Перемещает кнопку в случайное место подальше от курсора."""
        # Пробуем 20 раз найти подходящее место
        for _ in range(20):
            # Случайная позиция в пределах формы
            max_x = self.width() - self.btn.width() - 10
            max_y = self.height() - self.btn.height() - 10
            
            new_x = random.randint(10, max(11, max_x))
            new_y = random.randint(10, max(11, max_y))
            
            # Расстояние от нового места до курсора
            btn_center_x = new_x + self.btn.width() / 2
            btn_center_y = new_y + self.btn.height() / 2
            dx = mx - btn_center_x
            dy = my - btn_center_y
            new_distance = (dx * dx + dy * dy) ** 0.5
            
            # Если достаточно далеко — перемещаем
            if new_distance > self.danger_radius * 1.5:
                self.btn.move(new_x, new_y)
                return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RunawayButton()
    window.show()
    sys.exit(app.exec_())