class TablePrinter:
    @staticmethod
    def print_table(data, headers):
        if not data:
            print("\n Дані відсутні")
            return

        col_widths = [len(str(h)) for h in headers] #Рахуємо максимальну ширину для кожного стовпця

        normalized_data = []
        for row in data:
            safe_row = list(row)[:len(headers)]
            safe_row += [""] * (len(headers) - len(safe_row))
            normalized_data.append(safe_row)

        for row in normalized_data:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        row_format = " | ".join([f"{{:<{w}}}" for w in col_widths]) #Формуємо рядок так, щоб текст був рівненько по лівому краю
        row_format = f"| {row_format} |"

        separator = "+-" + "-+-".join(["-" * w for w in col_widths]) + "-+" #Створюємо горизонтальну лінію-розділювач

        print("\n" + separator)
        print(row_format.format(*headers))
        print(separator)

        for row in normalized_data:
            clean_row = [str(item) if item is not None else "-" for item in row]
            print(row_format.format(*clean_row))

        print(separator)
        print(f"Всього записів: {len(normalized_data)}\n")

    @staticmethod
    def print_apartment_info(details):
        """Виводимо детальну картку квартири: основні параметри + список мешканців, якщо вони є"""
        if not details:
            print("Квартиру не знайдено.")
            return

        apt = details['apartment']
        print(f"\n КВАРТИРА №{apt.number}")
        print(f"Поверх: {apt.floor}")
        print(f"Тип:    {apt.type.value}")
        print(f"Площа:  {apt.square_meters} м²")

        if details['residents']:
            print("ЗАРЕЄСТРОВАНІ МЕШКАНЦІ:")
            TablePrinter.print_table(
                details['residents'],
                ["ID", "ПІБ", "Email", "Телефон"]
            )
        else:
            print("Мешканці відсутні (квартира вільна).")