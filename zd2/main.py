import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import *
from task2 import Ui_Form
from task2_edit import Ui_Dialog


class EditDialog(QDialog, Ui_Dialog):
    """Диалог добавления/редактирования фильма."""
    def __init__(self, conn, film_id=None):
        super().__init__()
        self.setupUi(self)
        self.conn = conn
        self.film_id = film_id
        
        # Заполняем жанры
        cur = conn.cursor()
        cur.execute("SELECT id, title FROM genres ORDER BY title")
        for gid, gtitle in cur.fetchall():
            self.edit_genre.addItem(gtitle, gid)
        
        # Если редактируем - заполняем поля
        if film_id:
            self.setWindowTitle("Редактирование")
            cur.execute("SELECT title, year, genre, duration FROM films WHERE id=?", (film_id,))
            t, y, g, d = cur.fetchone()
            self.edit_title.setText(t)
            self.edit_year.setValue(y)
            self.edit_genre.setCurrentIndex(self.edit_genre.findData(g))
            self.edit_duration.setValue(d)
        else:
            self.setWindowTitle("Добавление")
        
        self.btn_ok.clicked.connect(self.save)
        self.btn_cancel.clicked.connect(self.reject)
    
    def save(self):
        """Сохраняет с валидацией."""
        title = self.edit_title.text().strip()
        year = self.edit_year.value()
        genre = self.edit_genre.currentData()
        duration = self.edit_duration.value()
        
        # Валидация
        if not title:
            QMessageBox.warning(self, "Ошибка", "Введите название!")
            return
        if year > datetime.now().year:
            QMessageBox.warning(self, "Ошибка", "Год в будущем!")
            return
        if duration <= 0:
            QMessageBox.warning(self, "Ошибка", "Длительность должна быть > 0!")
            return
        
        cur = self.conn.cursor()
        if self.film_id is None:
            cur.execute("INSERT INTO films (title, year, genre, duration) VALUES (?,?,?,?)",
                        (title, year, genre, duration))
        else:
            cur.execute("UPDATE films SET title=?, year=?, genre=?, duration=? WHERE id=?",
                        (title, year, genre, duration, self.film_id))
        self.conn.commit()
        self.accept()


class App(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.conn = sqlite3.connect("films_db.sqlite")
        
        # Кнопки
        self.btn_add.clicked.connect(self.add)
        self.btn_edit.clicked.connect(self.edit)
        self.btn_delete.clicked.connect(self.delete)
        self.btn_refresh.clicked.connect(self.load)
        
        self.load()
    
    def load(self):
        """Загружает фильмы в таблицу."""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT films.id AS ID,
                   films.title AS Название,
                   films.year AS Год,
                   genres.title AS Жанр,
                   films.duration AS "Длительность"
            FROM films
            LEFT JOIN genres ON films.genre = genres.id
        """)
        headers = [d[0] for d in cur.description]  # из БД
        rows = cur.fetchall()
        
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rows))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))
    
    def selected_id(self):
        """Возвращает ID выделенной строки."""
        row = self.table.currentRow()
        return int(self.table.item(row, 0).text()) if row >= 0 else None
    
    def add(self):
        if EditDialog(self.conn).exec_():
            self.load()
    
    def edit(self):
        fid = self.selected_id()
        if not fid:
            QMessageBox.warning(self, "Ошибка", "Выберите фильм!")
            return
        if EditDialog(self.conn, fid).exec_():
            self.load()
    
    def delete(self):
        fid = self.selected_id()
        if not fid:
            QMessageBox.warning(self, "Ошибка", "Выберите фильм!")
            return
        if QMessageBox.question(self, "?", f"Удалить ID={fid}?") == QMessageBox.Yes:
            self.conn.cursor().execute("DELETE FROM films WHERE id=?", (fid,))
            self.conn.commit()
            self.load()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec_())