import sqlite3

conn = sqlite3.connect("films_db.sqlite")
cur = conn.cursor()

# Удаляем старые таблицы, если есть
cur.execute("DROP TABLE IF EXISTS films")
cur.execute("DROP TABLE IF EXISTS genres")

# Таблица жанров
cur.execute("""
    CREATE TABLE genres (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL
    )
""")

# Таблица фильмов
cur.execute("""
    CREATE TABLE films (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        year INTEGER,
        genre INTEGER,
        duration INTEGER,
        FOREIGN KEY (genre) REFERENCES genres(id)
    )
""")

# Заполняем жанры
genres = [
    (1, "Комедия"),
    (2, "Драма"),
    (3, "Фантастика"),
    (4, "Боевик"),
    (5, "Триллер"),
]
cur.executemany("INSERT INTO genres VALUES (?, ?)", genres)

# Заполняем фильмы
films = [
    (1, "Иван Васильевич меняет профессию", 1973, 1, 93),
    (2, "Криминальное чтиво", 1994, 2, 154),
    (3, "Матрица", 1999, 3, 136),
    (4, "Терминатор 2", 1991, 4, 137),
    (5, "Форрест Гамп", 1994, 2, 142),
    (6, "Начало", 2010, 5, 148),
]
cur.executemany("INSERT INTO films VALUES (?, ?, ?, ?, ?)", films)

conn.commit()
conn.close()

print("БД films_db.sqlite создана!")
print("Таблицы: genres, films")
print("Жанры:", genres)
print("Фильмы:", len(films))