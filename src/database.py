import psycopg2
from psycopg2 import sql
import os
from src.config import DB_CONFIG
from src.utils.logger import logger


class DatabaseManager:
    _instance = None


    def __new__(cls):
        # Створюємо єдине підключення до бази, щоб не плодити зайві копії.
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._connection = None
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Створюємо базу, підключаємось та заливаємо схему таблиць
        try:
            self._create_db_if_not_exists()
            self._connection = psycopg2.connect(**DB_CONFIG)
            self._connection.autocommit = True
            self._run_sql_script('sql/schema.sql', "Схема")
            if self._is_database_empty():
                logger.info("База даних порожня. Виконується seed.sql...")
                self._run_sql_script('sql/seed.sql', "Демонстраційні дані")

        except Exception as e:
            logger.error(f"Критична помилка ініціалізації БД: {e}")
            raise

    def _create_db_if_not_exists(self):
        # Перевіряємо, чи існує наша база. Якщо ні — створюємо її з нуля
        temp_conn = psycopg2.connect(
            dbname='postgres',
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        temp_conn.autocommit = True
        db_name = DB_CONFIG['dbname']

        with temp_conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if not cur.fetchone():
                query = sql.SQL("CREATE DATABASE {db}").format(
                    db=sql.Identifier(db_name)
                )
                cur.execute(query)
                logger.info(f"База даних '{db_name}' успішно створена.")
        temp_conn.close()

    def _is_database_empty(self):
        # Перевіряємо наявність мешканців та квартир у базі
        query = "SELECT (SELECT COUNT(*) FROM residents) + (SELECT COUNT(*) FROM apartments)"
        with self._connection.cursor() as cur:
            cur.execute(query)
            return cur.fetchone()[0] == 0

    def _run_sql_script(self, file_path, description):
        # Читаємо SQL-файл і виконуємо його вміст
        if not os.path.exists(file_path):
            logger.warning(f"Файл {file_path} не знайдено. Пропуск ({description}).")
            return

        with self._connection.cursor() as cur:
            with open(file_path, 'r', encoding='utf-8') as f:
                cur.execute(f.read())
            logger.info(f"Успішно виконано: {description}")

    def get_connection(self):
        # Видаємо активне підключення. Якщо воно раптом "відпало" — перепідключаємось автоматично
        if self._connection is None or self._connection.closed != 0:
            self._connection = psycopg2.connect(**DB_CONFIG)
            self._connection.autocommit = True
        return self._connection