import sys
from dataclasses import astuple
from src.ui.printers import TablePrinter
from src.utils.exporter import Exporter
from src.utils.validators import get_int_input, validate_email, validate_phone, validate_date

class MainMenu:
    def __init__(self, house_service, report_service, resident_repo, apartment_repo):
        self.service = house_service
        self.report_service = report_service
        self.resident_repo = resident_repo
        self.apartment_repo = apartment_repo

    def show_main_menu(self):
        while True:
            print("\n СИСТЕМА УПРАВЛІННЯ БУДИНКОМ")
            print("1. Управління мешканцями")
            print("2. Управління квартирами")
            print("3. Операції (Переселення/Прив'язка)")
            print("4. Звіти та Експорт")
            print("0. Вихід")

            choice = input("\nОберіть дію: ")

            if choice == '1':
                self.resident_menu()
            elif choice == '2':
                self.apartment_menu()
            elif choice == '3':
                self.operations_menu()
            elif choice == '4':
                self.reports_menu()
            elif choice == '0':
                print("Завершення роботи.")
                sys.exit()
            else:
                print("Помилка: Невірний пункт.")


    def resident_menu(self):
        while True:
            print("\n УПРАВЛІННЯ МЕШКАНЦЯМИ")
            print("1. Додати мешканця")
            print("2. Список усіх мешканців")
            print("3. Видалити мешканця (Soft delete)")
            print("0. Назад")

            choice = input("\nВаш вибір: ")
            if choice == '1':
                name = input("ПІБ: ")

                # Валідація Email
                while True:
                    email = input("Email: ")
                    if validate_email(email): break
                    print("Невірний формат email (приклад: user@mail.com)")

                # Валідація телефону
                while True:
                    phone = input("Телефон (+380...): ")
                    if validate_phone(phone): break
                    print("Номер має бути у форматі +380XXXXXXXXX")

                # Валідація дати
                while True:
                    birth_date = input("Дата народження (РРРР-ММ-ДД): ")
                    if validate_date(birth_date): break
                    print("Невірний формат дати. Використовуйте РРРР-ММ-ДД")

                try:
                    self.resident_repo.create(name, email, phone, birth_date)
                    print(f"Мешканця '{name}' успішно додано!")
                except Exception as e:
                    print(f"Помилка бази даних: {e}")
            elif choice == '2':
                data = self.resident_repo.get_all()
                table_data = [astuple(r) for r in data]
                TablePrinter.print_table(table_data, ["ID", "ПІБ", "Email", "Телефон", "Дата народж."])
            elif choice == '3':
                res_id = get_int_input("Введіть ID для видалення: ")
                if self.resident_repo.soft_delete(res_id):
                    print("Мешканця видалено (soft delete).")
                else:
                    print("Помилка: Мешканця з таким ID не знайдено або він вже видалений.")
            elif choice == '0':
                break

    def apartment_menu(self):
        while True:
            print("\n УПРАВЛІННЯ КВАРТИРАМИ")
            print("1. Список усіх квартир")
            print("2. Деталі квартири (Мешканці)")
            print("3. Пошук квартир за поверхом")
            print("4. Пошук квартир за типом")
            print("0. Назад")

            choice = input("\nВаш вибір: ")

            if choice == '1':
                data = self.apartment_repo.get_all()
                table_data = [(a.id, a.number, a.floor, a.type.value, a.square_meters) for a in data]
                TablePrinter.print_table(table_data, ["ID", "№", "Поверх", "Тип", "Площа"])

            elif choice == '2':
                apt_id = get_int_input("ID квартири: ")
                details = self.service.get_apartment_details(apt_id)
                TablePrinter.print_apartment_info(details)

            elif choice == '3':
                floor = get_int_input("Введіть поверх: ")
                data = self.apartment_repo.get_by_floor(floor)
                table_data = [(a.id, a.number, a.floor, a.type.value, a.square_meters) for a in data]
                TablePrinter.print_table(table_data, ["ID", "№", "Поверх", "Тип", "Площа"])

            elif choice == '4':
                apt_type = input("Введіть тип (Студія, Однокімнатна, Двокімнатна і т.д.): ")
                data = self.apartment_repo.get_by_type(apt_type)
                table_data = [(a.id, a.number, a.floor, a.type.value, a.square_meters) for a in data]
                TablePrinter.print_table(table_data, ["ID", "№", "Поверх", "Тип", "Площа"])
            elif choice == '0':
                break

    def operations_menu(self):
        """Меню для руху мешканців: реєстрація в квартирі або переїзд з однієї в іншу"""
        while True:
            print("\n ОПЕРАЦІЇ")
            print("1. Закріпити мешканця за квартирою")
            print("2. Переселити мешканця")
            print("0. Назад")

            choice = input("\nВаш вибір: ")
            if choice == '1':
                res_id = get_int_input("ID мешканця: ")
                apt_id = get_int_input("ID квартири: ")
                try:
                    self.service.assign_resident_to_apartment(res_id, apt_id)
                    print("Успішно закріплено!")
                except Exception as e:
                    print(f"Помилка: {e}")
            elif choice == '2':
                res_id = get_int_input("ID мешканця: ")
                f_id = get_int_input("З ID квартири: ")
                t_id = get_int_input("В ID квартири: ")
                try:
                    self.service.move_resident(res_id, f_id, t_id)
                    print("Переселення завершено.")
                except Exception as e:
                    print(f"Помилка: {e}")
            elif choice == '0':
                break

    def reports_menu(self):
        while True:
            print("\n ЗВІТИ ТА ЕКСПОРТ")
            print("1. Повний список мешканців (на екран)")
            print("2. Повний список квартир (на екран)")
            print("3. Вільні квартири")
            print("4. Квартири на конкретному поверсі")
            print("5. Топ-5 найбільш заселених квартир (Бонус)")
            print("6. Експорт всіх мешканців (CSV + JSON)")
            print("0. Назад")

            choice = input("\nВаш вибір: ")

            if choice == '1':
                data = self.resident_repo.get_all()
                TablePrinter.print_table(data, ["ID", "ПІБ", "Email", "Телефон", "Дата народж."])

            elif choice == '2':
                data = self.apartment_repo.get_all()
                TablePrinter.print_table(data, ["ID", "№", "Поверх", "Тип"])

            elif choice == '3':
                data = self.apartment_repo.get_vacant()
                TablePrinter.print_table(data, ["ID", "№", "Поверх", "Тип"])

            elif choice == '4':
                floor = input("Введіть номер поверху: ")
                if floor.isdigit():
                    data = self.apartment_repo.get_by_floor(int(floor))
                    TablePrinter.print_table(data, ["ID", "№", "Поверх", "Тип"])
                else:
                    print("Помилка: Поверх має бути числом.")

            elif choice == '5':
                data = self.report_service.get_apartments_with_most_residents()
                TablePrinter.print_table(data, ["№ Квартири", "К-сть мешканців"])

            elif choice == '6':
                data = self.report_service.get_residents_for_export()

                json_path = Exporter.to_json(data, "residents_report")
                csv_path = Exporter.to_csv(data, "residents_report")

                print(f"Дані збережено у папку exports:")
                print(f"JSON: {json_path}")
                print(f"CSV: {csv_path}")

            elif choice == '0':
                break
            else:
                print("Невірний вибір, спробуйте ще раз.")