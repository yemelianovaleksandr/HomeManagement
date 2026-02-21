from src.database import DatabaseManager
from src.models.apartments import Apartment, AptType

class ApartmentRepository:
    def __init__(self):
        self.db = DatabaseManager()

    def get_all(self):
        # Дивимося список усіх квартир у будинку
        query = "SELECT id, number, floor, type, square_meters FROM apartments WHERE is_deleted = FALSE"
        conn = self.db.get_connection()
        with conn.cursor() as cur:
            cur.execute(query)
            return [
                Apartment(id=r[0], number=r[1], floor=r[2], type=AptType(r[3]), square_meters=r[4])
                for r in cur.fetchall()
            ]

    def get_by_id(self, apt_id):
        # Шукаємо конкретну квартиру за її номером в базі
        query = "SELECT id, number, floor, type, square_meters FROM apartments WHERE id = %s AND is_deleted = FALSE"
        conn = self.db.get_connection()
        with conn.cursor() as cur:
            cur.execute(query, (apt_id,))
            row = cur.fetchone()
            if row:
                return Apartment(id=row[0], number=row[1], floor=row[2], type=AptType(row[3]), square_meters=row[4])
            return None


    def get_by_floor(self, floor):
        # Дивимося, які квартири є на конкретному поверсі
        query = "SELECT id, number, floor, type, square_meters FROM apartments WHERE floor = %s AND is_deleted = FALSE"
        conn = self.db.get_connection()
        with conn.cursor() as cur:
            cur.execute(query, (floor,))
            return [
                Apartment(id=r[0], number=r[1], floor=r[2], type=AptType(r[3]), square_meters=r[4])
                for r in cur.fetchall()
            ]

    def get_by_type(self, apt_type):
        # Фільтруємо квартири за типом
        try:
            valid_type = AptType(apt_type)
        except ValueError:
            # Виводимо помилку та список доступних типів
            allowed_types = ", ".join([t.value for t in AptType])
            print(f"\nПомилка: Тип квартири '{apt_type}' не знайдено.")
            print(f"Доступні типи: {allowed_types}")
            return []

        # Фільтруємо квартири за підтвердженим типом
        query = "SELECT id, number, floor, type, square_meters FROM apartments WHERE type = %s::apartment_type AND is_deleted = FALSE"
        conn = self.db.get_connection()
        with conn.cursor() as cur:
            cur.execute(query, (valid_type.value,))
            return [
                Apartment(id=r[0], number=r[1], floor=r[2], type=AptType(r[3]), square_meters=r[4])
                for r in cur.fetchall()
            ]

    def get_top_populated(self, limit=5):
        # Шукаємо квартири з найбільшою кількістю мешканців
        query = """
                    SELECT a.number, COUNT(res.resident_id) as count
                    FROM apartments a
                    JOIN residency res ON a.id = res.apartment_id
                    JOIN residents r ON res.resident_id = r.id
                    WHERE a.is_deleted = FALSE AND r.is_deleted = FALSE
                    GROUP BY a.number
                    ORDER BY count DESC
                    LIMIT %s;
                """
        with self.db.get_connection().cursor() as cur:
            cur.execute(query, (limit,))
            return cur.fetchall()

    def get_vacant(self):
        # Отримуємо список вільних квартир
        query = """
            SELECT a.id, a.number, a.floor, a.type 
            FROM apartments a
            WHERE a.is_deleted = FALSE AND NOT EXISTS (
                SELECT 1 
                FROM residency res
                JOIN residents r ON res.resident_id = r.id
                WHERE res.apartment_id = a.id AND r.is_deleted = FALSE
            )
        """
        with self.db.get_connection().cursor() as cur:
            cur.execute(query)
            return cur.fetchall()