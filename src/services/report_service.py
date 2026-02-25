class ReportService:
    def __init__(self, resident_repo, apartment_repo):
        self.resident_repo = resident_repo
        self.apartment_repo = apartment_repo

    def get_residents_for_export(self) -> dict[str, tuple[list[str], list[list]]]:
        """Готуємо дані про мешканців у зручному форматі для вивантаження (CSV/JSON)"""
        raw_data = self.resident_repo.get_all()
        json_headers = ["ID", "Name", "Email", "Phone", "Birth Date"]
        json_rows = [
            [r.id, r.full_name, r.email, r.phone, r.birth_date.strftime("%d.%m.%Y") if r.birth_date else None]
                for r in raw_data
                ]

        csv_headers = ["ID", "ПІБ", "Електронна пошта", "Телефон", "Дата народження"]
        csv_rows = [
            [r.id, r.full_name, r.email, r.phone, r.birth_date.strftime("%d.%m.%Y") if r.birth_date else ""]
            for r in raw_data
        ]
        return {
        "json": (json_headers, json_rows),
        "csv": (csv_headers, csv_rows)
    }

    def get_apartments_with_most_residents(self) -> list[tuple[str, int]]:
        """Робимо топ-5 найбільш "густонаселених" квартир у будинку"""
        return self.apartment_repo.get_top_populated(limit=5)