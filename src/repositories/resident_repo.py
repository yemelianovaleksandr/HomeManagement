from src.database import DatabaseManager
from src.models.resident import Resident
from psycopg2 import sql
from datetime import date

class ResidentRepository:
    def __init__(self):
        self.db = DatabaseManager()

    def create(self, full_name:str, email:str, phone:str, birth_date:date) -> int:
        """Додаємо нового сусіда в нашу систему"""
        query = """
            INSERT INTO residents (full_name, email, phone, birth_date)
            VALUES (%s, %s, %s, %s) RETURNING id;
        """
        conn = self.db.get_connection()
        with conn.cursor() as cur:
            cur.execute(query, (full_name, email, phone, birth_date))
            return cur.fetchone()[0]

    def get_all(self, include_deleted:bool=False) -> list[Resident]:
        """Отримує список всіх мешканців"""
        if include_deleted:
            query = "SELECT id, full_name, email, phone, birth_date FROM residents ORDER BY id"
        else:
            query = "SELECT id, full_name, email, phone, birth_date FROM residents WHERE is_deleted = FALSE ORDER BY id"
        conn = self.db.get_connection()
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            return [
                Resident(id=row[0], full_name=row[1], email=row[2], phone=row[3], birth_date=row[4])
                for row in rows
            ]

    def get_by_id(self, resident_id:int) -> Resident | None:
        """Шукає конкретного мешканця за його унікальним ID"""
        query = "SELECT id, full_name, email, phone, birth_date FROM residents WHERE id = %s AND is_deleted = FALSE"
        conn = self.db.get_connection()
        with conn.cursor() as cur:
            cur.execute(query, (resident_id,))
            row = cur.fetchone()
            if row:
                return Resident(id=row[0], full_name=row[1], email=row[2], phone=row[3], birth_date=row[4])
            return None

    def get_by_apartment_id(self, apartment_id:int) -> list[tuple[int, str, str, str]]:
        """Дістаємо список усіх людей, які зараз прописані в цій квартирі"""
        query = """
            SELECT r.id, r.full_name, r.email, r.phone 
            FROM residents r
            JOIN residency res ON r.id = res.resident_id
            WHERE res.apartment_id = %s AND r.is_deleted = FALSE;
        """
        conn = self.db.get_connection()
        with conn.cursor() as cur:
            cur.execute(query, (apartment_id,))
            return cur.fetchall()

    def update(self, resident_id:int, **kwargs) -> bool:
        """Оновлюємо інформацію про людину"""
        if not kwargs:
            return False
        allowed_columns = {'full_name', 'email', 'phone', 'birth_date'}
        invalid_columns = set(kwargs.keys()) - allowed_columns
        if invalid_columns:
            raise ValueError(f"Недопустимі колонки для оновлення: {invalid_columns}")
        set_clauses = [
            sql.SQL("{} = %s").format(sql.Identifier(key))
            for key in kwargs.keys()
        ]
        query = sql.SQL("UPDATE residents SET {fields} WHERE id = %s AND is_deleted = FALSE").format(
            fields=sql.SQL(", ").join(set_clauses)
        )
        values = list(kwargs.values())
        values.append(resident_id)
        conn = self.db.get_connection()
        with conn.cursor() as cur:
            cur.execute(query, values)
            return cur.rowcount > 0

    def soft_delete(self, resident_id:int) -> bool:
        """Позначає мешканця як видаленого"""
        query = "UPDATE residents SET is_deleted = TRUE WHERE id = %s AND is_deleted = FALSE"
        conn = self.db.get_connection()
        with conn.cursor() as cur:
            cur.execute(query, (resident_id,))
            return cur.rowcount > 0
