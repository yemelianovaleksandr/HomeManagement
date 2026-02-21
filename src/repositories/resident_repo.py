from src.database import DatabaseManager
from src.models.resident import Resident

class ResidentRepository:
    def __init__(self):
        self.db = DatabaseManager()

    def create(self, full_name, email, phone, birth_date):
        # Додаємо нового сусіда в нашу систему
        query = """
            INSERT INTO residents (full_name, email, phone, birth_date)
            VALUES (%s, %s, %s, %s) RETURNING id;
        """
        conn = self.db.get_connection()
        with conn.cursor() as cur:
            cur.execute(query, (full_name, email, phone, birth_date))
            return cur.fetchone()[0]

    def get_all(self, include_deleted=False):
        # Отримує список всіх мешканців
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

    def get_by_id(self, resident_id):
        # Шукає конкретного мешканця за його унікальним ID
        query = "SELECT id, full_name, email, phone, birth_date FROM residents WHERE id = %s AND is_deleted = FALSE"
        conn = self.db.get_connection()
        with conn.cursor() as cur:
            cur.execute(query, (resident_id,))
            row = cur.fetchone()
            if row:
                return Resident(id=row[0], full_name=row[1], email=row[2], phone=row[3], birth_date=row[4])
            return None

    def get_by_apartment_id(self, apartment_id):
        # Дістаємо список усіх людей, які зараз прописані в цій квартирі
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

    def update(self, resident_id, **kwargs):
        # Оновлюємо інформацію про людину
        if not kwargs:
            return False

        fields = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(resident_id)

        query = f"UPDATE residents SET {fields} WHERE id = %s"
        conn = self.db.get_connection()
        with conn.cursor() as cur:
            cur.execute(query, values)
            return cur.rowcount > 0

    def soft_delete(self, resident_id):
        # Позначає мешканця як видаленого
        query = "UPDATE residents SET is_deleted = TRUE WHERE id = %s AND is_deleted = FALSE"
        conn = self.db.get_connection()
        with conn.cursor() as cur:
            cur.execute(query, (resident_id,))
            return cur.rowcount > 0
