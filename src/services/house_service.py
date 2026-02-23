from src.utils.logger import logger

class HouseService:
    def __init__(self, resident_repo, apartment_repo, residency_repo):
        self.resident_repo = resident_repo
        self.apartment_repo = apartment_repo
        self.residency_repo = residency_repo

    def assign_resident_to_apartment(self, resident_id, apartment_id):
        """Закріплюємо мешканця за квартирою в межах безпечної транзакції"""
        conn = self.residency_repo.db.get_transaction_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM residents WHERE id = %s AND is_deleted = FALSE", (resident_id,))
                    if not cur.fetchone():
                        raise Exception("Мешканця не знайдено (або його видалено)")
                    cur.execute("SELECT id FROM apartments WHERE id = %s AND is_deleted = FALSE", (apartment_id,))
                    if not cur.fetchone():
                        raise Exception("Квартиру не знайдено (або її видалено)")
                    cur.execute(
                        "INSERT INTO residency (resident_id, apartment_id) VALUES (%s, %s)",
                        (resident_id, apartment_id)
                    )
            logger.info(f"Мешканець {resident_id} закріплений за квартирою {apartment_id}.")
        except Exception as e:
            logger.error(f"Помилка при закріпленні мешканця: {e}")
            raise e
        finally:
            conn.close()

    def move_resident(self, resident_id, from_apt_id, to_apt_id):
        """Переселяє мешканця з однієї квартири в іншу. Виконує всі необхідні перевірки перед операцією."""
        if from_apt_id == to_apt_id:
            raise ValueError("Неможливо переселити в ту саму квартиру (from == to)")
        resident = self.resident_repo.get_by_id(resident_id)
        if resident is None:
            raise ValueError(f"Мешканця з ID {resident_id} не знайдено або він видалений")
        from_apt = self.apartment_repo.get_by_id(from_apt_id)
        if from_apt is None:
            raise ValueError(f"Квартиру-джерело (ID {from_apt_id}) не знайдено або видалено")
        to_apt = self.apartment_repo.get_by_id(to_apt_id)
        if to_apt is None:
            raise ValueError(f"Квартиру-призначення (ID {to_apt_id}) не знайдено або видалено")
        conn = self.residency_repo.db.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1 FROM residency
                    WHERE resident_id = %s AND apartment_id = %s
                    """,
                    (resident_id, from_apt_id)
                )
                if not cur.fetchone():
                    raise ValueError(
                        f"Мешканець ID {resident_id} не прописаний у квартирі ID {from_apt_id}"
                    )
        finally:
            pass
        conn_tx = self.residency_repo.db.get_transaction_connection()
        try:
            with conn_tx:
                with conn_tx.cursor() as cur:
                    cur.execute(
                        "DELETE FROM residency WHERE resident_id = %s AND apartment_id = %s",
                        (resident_id, from_apt_id)
                    )
                    cur.execute(
                        "INSERT INTO residency (resident_id, apartment_id) VALUES (%s, %s)",
                        (resident_id, to_apt_id)
                    )
            logger.info(
                f"Мешканець {resident_id} ({resident.full_name}) "
                f"переселений з квартири {from_apt_id} → {to_apt_id}"
            )
            return True
        except Exception as e:
            logger.error(f"Помилка при переселенні мешканця {resident_id}: {e}")
            raise
        finally:
            conn_tx.close()

    def unassign_resident(self, resident_id, apartment_id):
        """Просто виписуємо мешканця з квартири"""
        try:
            if self.residency_repo.remove_link(resident_id, apartment_id):
                logger.info(f"Мешканець {resident_id} відкріплений від квартири {apartment_id}.")
                return True
            return  False
        except Exception as e:
            logger.error(f"Помилка відкріплення: {e}")
            return False

    def get_apartment_details(self, apartment_id):
        """Отримує деталі квартири та список її поточних мешканців"""
        apt = self.apartment_repo.get_by_id(apartment_id)
        if not apt:
            return None

        residents = self.resident_repo.get_by_apartment_id(apartment_id)
        return {
            "apartment": apt,
            "residents": residents,
            "count": len(residents)
        }

    def delete_resident(self, resident_id):
        """Відкріплюємо від квартир і видаляємо"""
        conn = self.resident_repo.db.get_transaction_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM residency WHERE resident_id = %s", (resident_id,))
                    cur.execute("UPDATE residents SET is_deleted = TRUE WHERE id = %s AND is_deleted = FALSE",
                                (resident_id,))
                    if cur.rowcount == 0:
                        raise Exception("Мешканця не знайдено або він вже видалений")
            logger.info(f"Мешканця {resident_id} видалено та відкріплено від квартир.")
            return True
        except Exception as e:
            logger.error(f"Помилка при видаленні мешканця {resident_id}: {e}")
            return False
        finally:
            conn.close()