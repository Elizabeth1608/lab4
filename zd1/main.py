import sys
import csv
import re
from PyQt5.QtWidgets import (QApplication, QWidget, QTableWidgetItem,
                              QMessageBox, QHeaderView)
from PyQt5.QtGui import QColor
from task1 import Ui_Form


class OlympiadApp(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.all_data = []
        
        # Настраиваем таблицу
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Логин", "ФИО", "Балл"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        
        # Загружаем CSV
        self.load_csv("rez.csv")
        
        # Заполняем выпадающие списки
        self.fill_filters()
        
        # Подключаем фильтры
        self.combo_school.currentIndexChanged.connect(self.apply_filter)
        self.combo_class.currentIndexChanged.connect(self.apply_filter)
        
        # Показываем все данные
        self.apply_filter()
    
    def load_csv(self, filename):
        """Читает CSV-файл с результатами олимпиады."""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    login = row.get("login", "").strip()
                    
                    match = re.match(r"sh-kaluga16-(\d+)-(\d+)-(\d+)", login)
                    if not match:
                        continue
                    
                    school = match.group(1)
                    klass = match.group(2)
                    
                    try:
                        score = int(row.get("Score", "0").strip())
                    except ValueError:
                        score = 0
                    
                    self.all_data.append({
                        "login": login,
                        "name": row.get("user_name", "").strip().strip('"'),
                        "score": score,
                        "school": school,
                        "klass": klass,
                    })
            
            print(f"Загружено записей: {len(self.all_data)}")
        
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить CSV:\n{e}")
    
    def fill_filters(self):
        """Заполняет ComboBox уникальными значениями школ и классов."""
        schools = sorted({d["school"] for d in self.all_data})
        klasses = sorted({d["klass"] for d in self.all_data})
        
        self.combo_school.clear()
        self.combo_school.addItem("Все")
        for s in schools:
            self.combo_school.addItem(s)
        
        self.combo_class.clear()
        self.combo_class.addItem("Все")
        for k in klasses:
            self.combo_class.addItem(k)
    
    def apply_filter(self):
        """Фильтрует данные и заполняет таблицу с раскраской призёров."""
        school_filter = self.combo_school.currentText()
        class_filter = self.combo_class.currentText()
        
        filtered = []
        for d in self.all_data:
            if school_filter != "Все" and d["school"] != school_filter:
                continue
            if class_filter != "Все" and d["klass"] != class_filter:
                continue
            filtered.append(d)
        
        # Сортируем по баллам (убывание)
        filtered.sort(key=lambda x: -x["score"])
        
        # Определяем места (с учётом одинаковых баллов)
        places = {}
        place_counter = 0
        last_score = None
        for i, d in enumerate(filtered):
            if d["score"] != last_score:
                place_counter = i + 1
                last_score = d["score"]
            places[d["login"]] = place_counter
        
        # Заполняем таблицу
        self.table.setRowCount(0)
        for d in filtered:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(d["login"]))
            self.table.setItem(row, 1, QTableWidgetItem(d["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(str(d["score"])))
            
            # Раскраска призёров
            place = places[d["login"]]
            if place == 1:
                color = QColor(255, 215, 0)     # золотой
            elif place == 2:
                color = QColor(192, 192, 192)   # серебряный
            elif place == 3:
                color = QColor(205, 127, 50)    # бронзовый
            else:
                color = None
            
            if color:
                for col in range(3):
                    self.table.item(row, col).setBackground(color)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OlympiadApp()
    window.show()
    sys.exit(app.exec_())