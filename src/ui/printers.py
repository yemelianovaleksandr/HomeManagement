class TablePrinter:
    @staticmethod
    def print_table(data, headers):
        if not data:
            print("\n Дані відсутні")
            return

        col_widths = []
        for i, header in enumerate(headers):
            max_val = len(str(header))
            for row in data:
                val = str(row[i]) if i < len(row) else ""
                if len(val) > max_val:
                    max_val = len(val)
            col_widths.append(max_val)

        separator = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"

        print(separator)
        header_row = "|" + "|".join([f" {str(h).ljust(col_widths[i])} " for i, h in enumerate(headers)]) + "|"
        print(header_row)
        print(separator)
        for row in data:
            data_row = "|" + "|".join([f" {str(row[i]).ljust(col_widths[i])} " for i in range(len(headers))]) + "|"
            print(data_row)
        print(separator)

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