from src.database import DatabaseManager

class ResidencyRepository:
    def __init__(self):
        self.db = DatabaseManager()

    def add_link(self, resident_id:int, apartment_id:int) -> bool:
        """Закріплюємо мешканця за конкретною квартирою"""
        query = "INSERT INTO residency (resident_id, apartment_id) VALUES (%s, %s)"
        conn = self.db.get_connection()
        with conn.cursor() as cur:
            cur.execute(query, (resident_id, apartment_id))
            return cur.rowcount > 0

    def remove_link(self, resident_id:int, apartment_id:int) -> bool:
        """Видаляємо зв'язок між мешканцем та квартирою (відкріплення)"""
        query = "DELETE FROM residency WHERE resident_id = %s AND apartment_id = %s"
        conn = self.db.get_connection()
        with conn.cursor() as cur:
            cur.execute(query, (resident_id, apartment_id))
            return cur.rowcount > 0