class ReportService:
    def __init__(self, resident_repo, apartment_repo):
        self.resident_repo = resident_repo
        self.apartment_repo = apartment_repo

    def get_residents_for_export(self):
        """Готуємо дані про мешканців у зручному форматі для вивантаження (CSV/JSON)"""
        raw_data = self.resident_repo.get_all()
        return [
            {"id": r.id, "name": r.full_name, "email": r.email, "phone": r.phone}
            for r in raw_data
        ]

    def get_apartments_with_most_residents(self):
        """Робимо топ-5 найбільш "густонаселених" квартир у будинку"""
        return self.apartment_repo.get_top_populated(limit=5)