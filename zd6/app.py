import sys
import os
import shutil
import hashlib
import sqlite3
from PyQt5.QtWidgets import (QApplication, QDialog, QMainWindow, QWidget,
                              QTableWidgetItem, QMessageBox, QFileDialog,
                              QHeaderView)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt

from login import Ui_Dialog as LoginUI
from main import Ui_MainWindow as MainUI
from edit_book import Ui_Dialog as EditBookUI


DB_PATH = "library.db"
IMAGES_DIR = "images"
DEFAULT_IMAGE = "images/default.png"


def hash_password(password):
    """Хеширует пароль через SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def get_default_image_path():
    """Путь к картинке-заглушке. Создаёт её, если нет."""
    if not os.path.exists(DEFAULT_IMAGE):
        from PIL import Image, ImageDraw
        os.makedirs(IMAGES_DIR, exist_ok=True)
        img = Image.new("RGB", (150, 200), (200, 200, 200))
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 140, 190], outline=(100, 100, 100), width=2)
        draw.text((45, 95), "НЕТ ФОТО", fill=(80, 80, 80))
        img.save(DEFAULT_IMAGE)
    return DEFAULT_IMAGE

# ФОРМА АВТОРИЗАЦИИ
class LoginDialog(QDialog, LoginUI):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Авторизация")
        self.conn = sqlite3.connect(DB_PATH)
        self.user_logged_in = False
        
        self.btn_login.clicked.connect(self.login)
        self.btn_register.clicked.connect(self.register)
    
    def login(self):
        """Проверяет логин и пароль."""
        login = self.edit_login.text().strip()
        password = self.edit_password.text()
        
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль!")
            return
        
        cur = self.conn.cursor()
        cur.execute("SELECT id, password_hash FROM users WHERE login = ?", (login,))
        row = cur.fetchone()
        
        if not row:
            QMessageBox.warning(self, "Ошибка", "Пользователь не найден!")
            return
        
        if row[1] != hash_password(password):
            QMessageBox.warning(self, "Ошибка", "Неверный пароль!")
            return
        
        self.user_logged_in = True
        self.accept()
    
    def register(self):
        """Регистрирует нового пользователя."""
        login = self.edit_login.text().strip()
        password = self.edit_password.text()
        
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль!")
            return
        
        if len(password) < 3:
            QMessageBox.warning(self, "Ошибка", "Пароль слишком короткий!")
            return
        
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM users WHERE login = ?", (login,))
        if cur.fetchone():
            QMessageBox.warning(self, "Ошибка", "Такой логин уже занят!")
            return
        
        try:
            cur.execute("INSERT INTO users (login, password_hash) VALUES (?, ?)",
                        (login, hash_password(password)))
            self.conn.commit()
            QMessageBox.information(self, "Готово", f"Пользователь {login} создан!")
            self.edit_password.clear()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

# ДИАЛОГ ДОБАВЛЕНИЯ/РЕДАКТИРОВАНИЯ КНИГИ
class BookEditDialog(QDialog, EditBookUI):
    def __init__(self, conn, book_id=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.conn = conn
        self.book_id = book_id
        self.image_path = None
        
        self.btn_image.clicked.connect(self.choose_image)
        self.btn_ok.clicked.connect(self.save)
        self.btn_cancel.clicked.connect(self.reject)
        
        # Картинка-заглушка
        self.set_preview(get_default_image_path())
        
        if book_id is not None:
            self.setWindowTitle("Редактирование книги")
            self.load_book()
        else:
            self.setWindowTitle("Добавление книги")
    
    def load_book(self):
        cur = self.conn.cursor()
        cur.execute("SELECT title, author, year, genre, image_path FROM books WHERE id=?",
                    (self.book_id,))
        row = cur.fetchone()
        if row:
            self.edit_title.setText(row[0])
            self.edit_author.setText(row[1])
            self.edit_year.setValue(row[2])
            self.edit_genre.setText(row[3] or "")
            if row[4] and os.path.exists(row[4]):
                self.image_path = row[4]
                self.set_preview(row[4])
    
    def set_preview(self, path):
        """Показывает картинку в preview."""
        pixmap = QPixmap(path)
        if pixmap.isNull():
            pixmap = QPixmap(get_default_image_path())
        self.image_preview.setPixmap(pixmap.scaled(
            self.image_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
    
    def choose_image(self):
        """Диалог выбора картинки."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать картинку", "",
            "Изображения (*.png *.jpg *.jpeg *.bmp)"
        )
        if not path:
            return
        
        # Копируем картинку в папку images
        os.makedirs(IMAGES_DIR, exist_ok=True)
        ext = os.path.splitext(path)[1]
        new_name = f"book_{hashlib.md5(path.encode()).hexdigest()[:8]}{ext}"
        new_path = os.path.join(IMAGES_DIR, new_name)
        
        try:
            shutil.copy(path, new_path)
            self.image_path = new_path
            self.set_preview(new_path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось скопировать:\n{e}")
    
    def save(self):
        """Сохраняет книгу с валидацией."""
        title = self.edit_title.text().strip()
        author = self.edit_author.text().strip()
        year = self.edit_year.value()
        genre = self.edit_genre.text().strip()
        image = self.image_path or get_default_image_path()
        
        if not title or not author:
            QMessageBox.warning(self, "Ошибка", "Название и автор обязательны!")
            return
        
        if year < 1000 or year > 2100:
            QMessageBox.warning(self, "Ошибка", "Год должен быть в диапазоне 1000–2100!")
            return
        
        cur = self.conn.cursor()
        try:
            if self.book_id is None:
                cur.execute("""
                    INSERT INTO books (title, author, year, genre, image_path)
                    VALUES (?, ?, ?, ?, ?)
                """, (title, author, year, genre, image))
            else:
                cur.execute("""
                    UPDATE books SET title=?, author=?, year=?, genre=?, image_path=?
                    WHERE id=?
                """, (title, author, year, genre, image, self.book_id))
            self.conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))

# ГЛАВНОЕ ОКНО
class MainWindow(QMainWindow, MainUI):
    def __init__(self, conn):
        super().__init__()
        self.setupUi(self)
        self.conn = conn
        self.setWindowTitle("Каталог библиотеки")
        
        # placeholder для поиска
        self.edit_search.setPlaceholderText("Поиск...")
        
        # Настройка таблицы
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Название", "Автор", "Год", "Жанр", "Обложка"])
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setSelectionMode(self.table.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(120)  # высота строк
        
        # Кнопки
        self.btn_add.clicked.connect(self.add_book)
        self.btn_edit.clicked.connect(self.edit_book)
        self.btn_delete.clicked.connect(self.delete_book)
        self.btn_search.clicked.connect(self.search)
        self.btn_clear.clicked.connect(self.clear_search)
        
        self.load_data()
    
    def load_data(self, query="", search_by="title"):
        """Загружает книги из БД (с фильтром)."""
        cur = self.conn.cursor()
        
        if query:
            if search_by == "author":
                cur.execute(
                    "SELECT id, title, author, year, genre, image_path FROM books WHERE author LIKE ?",
                    (f"%{query}%",)
                )
            else:
                cur.execute(
                    "SELECT id, title, author, year, genre, image_path FROM books WHERE title LIKE ?",
                    (f"%{query}%",)
                )
        else:
            cur.execute("SELECT id, title, author, year, genre, image_path FROM books")
        
        rows = cur.fetchall()
        
        self.table.setRowCount(0)
        for row in rows:
            book_id, title, author, year, genre, image_path = row
            r = self.table.rowCount()
            self.table.insertRow(r)
            
            self.table.setItem(r, 0, QTableWidgetItem(title))
            self.table.setItem(r, 1, QTableWidgetItem(author))
            self.table.setItem(r, 2, QTableWidgetItem(str(year)))
            self.table.setItem(r, 3, QTableWidgetItem(genre or ""))
            
            # Картинка
            if image_path and os.path.exists(image_path):
                pix = QPixmap(image_path)
            else:
                pix = QPixmap(get_default_image_path())
            
            if not pix.isNull():
                pix = pix.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label_item = QTableWidgetItem()
                label_item.setData(Qt.DecorationRole, pix)
                self.table.setItem(r, 4, label_item)
            
            # Сохраняем ID книги в UserRole первого item
            self.table.item(r, 0).setData(Qt.UserRole, book_id)
    
    def get_selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).data(Qt.UserRole)
    
    def add_book(self):
        dlg = BookEditDialog(self.conn, None, self)
        if dlg.exec_() == QDialog.Accepted:
            self.load_data()
    
    def edit_book(self):
        book_id = self.get_selected_id()
        if book_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу!")
            return
        dlg = BookEditDialog(self.conn, book_id, self)
        if dlg.exec_() == QDialog.Accepted:
            self.load_data()
    
    def delete_book(self):
        book_id = self.get_selected_id()
        if book_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу!")
            return
        if QMessageBox.question(self, "?", "Удалить книгу?") == QMessageBox.Yes:
            self.conn.cursor().execute("DELETE FROM books WHERE id=?", (book_id,))
            self.conn.commit()
            self.load_data()
    
    def search(self):
        """Поиск по названию или автору."""
        query = self.edit_search.text().strip()
        if not query:
            self.load_data()
            return
        search_by = "author" if self.combo_search.currentIndex() == 1 else "title"
        self.load_data(query, search_by)
    
    def clear_search(self):
        self.edit_search.clear()
        self.load_data()


# ЗАПУСК ПРИЛОЖЕНИЯ
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 1. Показать форму авторизации
    login_dlg = LoginDialog()
    if login_dlg.exec_() != QDialog.Accepted:
        sys.exit(0)
    
    # 2. Открыть главное окно
    conn = sqlite3.connect(DB_PATH)
    window = MainWindow(conn)
    window.show()
    sys.exit(app.exec_())