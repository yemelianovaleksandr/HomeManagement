import sys
from dataclasses import astuple
from src.ui.printers import TablePrinter
from src.utils.exporter import Exporter
from src.utils.validators import get_int_input, validate_email, validate_phone, validate_date, get_float_input
from src.models.apartments import AptType
from datetime import datetime

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
            print("4. Редагувати контактні дані")
            print("5. Деталі мешканця за ID")
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
                if self.service.delete_resident(res_id):
                    print("Мешканця видалено та відкріплено від усіх квартир.")
                else:
                    print("Помилка: Мешканця з таким ID не знайдено або він вже видалений.")
            elif choice == '4':
                res_id = get_int_input("Введіть ID мешканця: ")
                if not self.resident_repo.get_by_id(res_id):
                    print("Мешканця не знайдено.")
                    continue

                print("Залиште поле порожнім, якщо не хочете його змінювати.")
                new_phone = input("Новий телефон (+380...): ").strip()
                new_email = input("Новий Email: ").strip()

                updates = {}
                if new_phone and validate_phone(new_phone):
                    updates['phone'] = new_phone
                elif new_phone:
                    print("Телефон проігноровано (невірний формат).")

                if new_email and validate_email(new_email):
                    updates['email'] = new_email
                elif new_email:
                    print("Email проігноровано (невірний формат).")
                if updates:
                    self.resident_repo.update(res_id, **updates)
                    print("Дані успішно оновлено!")
                else:
                    print("Немає коректних даних для оновлення.")
            elif choice == '5':
                res_id = get_int_input("Введіть ID мешканця: ")

                resident = self.resident_repo.get_by_id(res_id)
                if not resident:
                    print("Мешканця не знайдено або він видалений.")
                    continue

                print("\nДЕТАЛІ МЕШКАНЦЯ")
                print(f"ID: {resident.id}")
                print(f"ПІБ: {resident.full_name}")
                print(f"Email: {resident.email or 'не вказано'}")
                print(f"Телефон: {resident.phone}")
                print(
                    f"Дата народження: {resident.birth_date.strftime('%d.%m.%Y') if resident.birth_date else 'не вказано'}")
                print(f"Статус: {'Активний' if not resident.is_deleted else 'Видалений'}")

                conn = self.resident_repo.db.get_connection()
                with conn.cursor() as cur:
                    cur.execute("""
                                SELECT a.id, a.number, a.floor, a.type, r.move_in_date
                                FROM residency r
                                JOIN apartments a ON r.apartment_id = a.id
                                WHERE r.resident_id = %s AND a.is_deleted = FALSE
                                ORDER BY r.move_in_date DESC
                            """, (res_id,))
                    apartments = cur.fetchall()

                if apartments:
                    print("\nПоточні квартири (прописаний):")
                    for apt in apartments:
                        apt_id, number, floor, apt_type, move_date = apt
                        print(
                            f"  - Квартира №{number} (ID {apt_id}), поверх {floor}, тип: {apt_type}, заселений: {move_date.strftime('%d.%m.%Y')}")
                else:
                    print("\nМешканець ніде не прописаний (немає активних квартир).")

            elif choice == '0':
                break
            else:
                print("Невірний вибір.")

    def apartment_menu(self):
        while True:
            print("\n УПРАВЛІННЯ КВАРТИРАМИ")
            print("1. Додати квартиру")
            print("2. Список усіх квартир")
            print("3. Деталі квартири (Мешканці)")
            print("4. Пошук квартир за поверхом")
            print("5. Пошук квартир за типом")
            print("6. Видалити квартиру (Soft delete)")
            print("7. Редагувати квартиру")
            print("0. Назад")

            choice = input("\nВаш вибір: ")

            if choice == '1':
                number = input("Номер квартири: ").strip()
                if not number:
                    print("Номер квартири не може бути порожнім.")
                    continue

                floor = get_int_input("Поверх: ")
                allowed_types = [e.value for e in AptType]
                print("\nДозволені типи квартир:")
                for i, t in enumerate(allowed_types, 1):
                    print(f"  {i}. {t}")
                while True:
                    type_input = input("\nВиберіть тип квартири (введіть номер або повний текст): ").strip()
                    selected_type = None
                    if type_input.isdigit():
                        idx = int(type_input) - 1
                        if 0 <= idx < len(allowed_types):
                            selected_type = allowed_types[idx]
                    else:
                        type_lower = type_input.lower()
                        for t in allowed_types:
                            if t.lower() == type_lower:
                                selected_type = t
                                break
                    if selected_type:
                        break
                    else:
                        print("Невірний вибір. Спробуйте ще раз (номер або назву типу).")
                sq_meters = get_float_input("Площа (м²): ")
                try:
                    created_id = self.apartment_repo.create(number, floor, selected_type, sq_meters)
                    print(f"Квартиру №{number} (ID {created_id}) успішно додано!")
                except Exception as e:
                    print(f"Помилка при додаванні квартири: {e}")

            elif choice == '2':
                data = self.apartment_repo.get_all()
                table_data = [(a.id, a.number, a.floor, a.type.value, a.square_meters) for a in data]
                TablePrinter.print_table(table_data, ["ID", "№", "Поверх", "Тип", "Площа"])

            elif choice == '3':
                apt_id = get_int_input("ID квартири: ")
                details = self.service.get_apartment_details(apt_id)
                TablePrinter.print_apartment_info(details)

            elif choice == '4':
                floor = get_int_input("Введіть поверх: ")
                data = self.apartment_repo.get_by_floor(floor)
                table_data = [(a.id, a.number, a.floor, a.type.value, a.square_meters) for a in data]
                TablePrinter.print_table(table_data, ["ID", "№", "Поверх", "Тип", "Площа"])

            elif choice == '5':
                apt_type = input("Введіть тип (Студія, Однокімнатна, Двокімнатна і т.д.): ")
                data = self.apartment_repo.get_by_type(apt_type)
                table_data = [(a.id, a.number, a.floor, a.type.value, a.square_meters) for a in data]
                TablePrinter.print_table(table_data, ["ID", "№", "Поверх", "Тип", "Площа"])

            elif choice == '6':
                apt_id = get_int_input("Введіть ID квартири для видалення: ")
                if self.apartment_repo.delete(apt_id):
                    print("Квартиру видалено (soft delete).")
                else:
                    print("Помилка при видаленні.")
            elif choice == "7":
                apt_id = get_int_input("Введіть ID квартири для редагування: ")
                conn = self.apartment_repo.db.get_connection()
                with conn.cursor() as cur:
                    cur.execute("""
                            SELECT number, floor, type, square_meters 
                            FROM apartments 
                            WHERE id = %s AND is_deleted = FALSE
                        """, (apt_id,))
                    row = cur.fetchone()

                if not row:
                    print("Квартиру не знайдено або вона видалена.")
                    continue

                current_number, current_floor, current_type, current_sq = row

                print("\nПоточні дані:")
                print(f"  Номер : {current_number}")
                print(f"  Поверх: {current_floor}")
                print(f"  Тип   : {current_type}")
                print(f"  Площа : {current_sq} м²")

                allowed_types = ["Студія", "Однокімнатна", "Двокімнатна", "Трикімнатна", "Чотирикімнатна"]
                print("\nДоступні типи:")
                for i, t in enumerate(allowed_types, 1):
                    print(f"  {i}. {t}")

                print("\nНові значення (Enter — залишити без змін):")

                number = input(f"Номер квартири [{current_number}]: ").strip() or None

                # Парсинг поверху
                floor = None
                floor_str = input(f"Поверх [{current_floor}]: ").strip()
                if floor_str:
                    try:
                        floor = int(floor_str)
                        if floor < 0:
                            print("Поверх не може бути від'ємним.")
                            continue
                    except ValueError:
                        print("Поверх має бути цілим числом.")
                        continue

                # Валідація типу квартири
                apt_type = None
                type_input = input(f"Тип [{current_type}]: ").strip()
                if type_input:
                    if type_input.isdigit():
                        try:
                            idx = int(type_input) - 1
                            if 0 <= idx < len(allowed_types):
                                apt_type = allowed_types[idx]
                            else:
                                print(f"Номер типу повинен бути від 1 до {len(allowed_types)}")
                                continue
                        except:
                            print("Невірний номер типу.")
                            continue
                    else:
                        found = False
                        for t in allowed_types:
                            if t.lower() == type_input.lower():
                                apt_type = t
                                found = True
                                break
                        if not found:
                            print("Невірний тип. Введіть номер або точну назву з списку.")
                            continue

                # Парсинг площі
                sq_meters = None
                sq_str = input(f"Площа (м²) [{current_sq}]: ").strip()
                if sq_str:
                    sq_str = sq_str.replace(',', '.')
                    try:
                        sq_meters = float(sq_str)
                        if sq_meters <= 0:
                            print("Площа має бути більшою за 0.")
                            continue
                    except ValueError:
                        print("Площа має бути числом (наприклад 45.5 або 45,5).")
                        continue

                if number is None and floor is None and apt_type is None and sq_meters is None:
                    print("Жодне поле не змінено. Оновлення скасовано.")
                    continue

                try:
                    updated = self.apartment_repo.update(
                        apt_id=apt_id,
                        number=number,
                        floor=floor,
                        apt_type=apt_type,
                        square_meters=sq_meters
                    )
                    if updated:
                        print("Квартиру успішно оновлено!")
                    else:
                        print("Не вдалося оновити (можливо квартира видалена або нічого не змінилося).")
                except Exception as e:
                    print(f"Помилка при оновленні квартири: {e}")

    def operations_menu(self):
        """Меню для руху мешканців: реєстрація в квартирі або переїзд з однієї в іншу"""
        while True:
            print("\n ОПЕРАЦІЇ")
            print("1. Закріпити мешканця за квартирою")
            print("2. Переселити мешканця")
            print("3. Відкріпити мешканця (виселення)")
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
            elif choice == '3':
                res_id = get_int_input("ID мешканця: ")
                apt_id = get_int_input("ID квартири: ")
                if self.service.unassign_resident(res_id, apt_id):
                    print("Мешканця успішно відкріплено від квартири.")
                else:
                    print("Не вдалося відкріпити (можливо, зв'язок не існує).")
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
                table_data = [astuple(r) for r in data]
                TablePrinter.print_table(table_data, ["ID", "ПІБ", "Email", "Телефон", "Дата народж."])

            elif choice == '2':
                data = self.apartment_repo.get_all()
                table_data = [(a.id, a.number, a.floor, a.type.value) for a in data]
                TablePrinter.print_table(table_data, ["ID", "№", "Поверх", "Тип"])

            elif choice == '3':
                data = self.apartment_repo.get_vacant()
                TablePrinter.print_table(data, ["ID", "№", "Поверх", "Тип"])

            elif choice == '4':
                floor = input("Введіть номер поверху: ")
                if floor.isdigit():
                    data = self.apartment_repo.get_by_floor(int(floor))
                    table_data = [(a.id, a.number, a.floor, a.type.value) for a in data]
                    TablePrinter.print_table(table_data, ["ID", "№", "Поверх", "Тип"])
                else:
                    print("Помилка: Поверх має бути числом.")

            elif choice == '5':
                data = self.report_service.get_apartments_with_most_residents()
                TablePrinter.print_table(data, ["№ Квартири", "К-сть мешканців"])

            elif choice == '6':
                export_data = self.report_service.get_residents_for_export()

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name = f"residents_report_{timestamp}"

                json_headers, json_rows = export_data["json"]
                json_data = [dict(zip(json_headers, row)) for row in json_rows]
                json_path = Exporter.to_json(json_data, base_name)

                csv_headers, csv_rows = export_data["csv"]
                csv_path = Exporter.to_csv(csv_rows, base_name, headers=csv_headers)
                print(f"Дані збережено у папку exports:")
                print(f"JSON: {json_path}")
                print(f"CSV: {csv_path}")
            elif choice == '0':
                break
            else:
                print("Невірний вибір, спробуйте ще раз.")