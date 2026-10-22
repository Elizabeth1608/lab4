import sqlite3
import hashlib

conn = sqlite3.connect("library.db")
cur = conn.cursor()

# Удаляем старые таблицы
cur.execute("DROP TABLE IF EXISTS users")
cur.execute("DROP TABLE IF EXISTS books")

# Таблица пользователей
cur.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
""")

# Таблица книг
cur.execute("""
    CREATE TABLE books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        year INTEGER,
        genre TEXT,
        image_path TEXT
    )
""")

# Тестовый пользователь (login=admin, password=123)
password_hash = hashlib.sha256("123".encode()).hexdigest()
cur.execute("INSERT INTO users (login, password_hash) VALUES (?, ?)",
            ("admin", password_hash))

# Тестовые книги
books = [
    ("Война и мир", "Лев Толстой", 1869, "Роман", None),
    ("Преступление и наказание", "Фёдор Достоевский", 1866, "Роман", None),
    ("Мастер и Маргарита", "Михаил Булгаков", 1967, "Роман", None),
    ("1984", "Джордж Оруэлл", 1949, "Антиутопия", None),
    ("Гарри Поттер", "Джоан Роулинг", 1997, "Фэнтези", None),
]
cur.executemany(
    "INSERT INTO books (title, author, year, genre, image_path) VALUES (?, ?, ?, ?, ?)",
    books
)

conn.commit()
conn.close()

print("БД library.db создана!")
print("Тестовый пользователь: login=admin, password=123")
print(f"Добавлено книг: {len(books)}")