import sys
from src.repositories.resident_repo import ResidentRepository
from src.repositories.apartment_repo import ApartmentRepository
from src.repositories.residency_repo import ResidencyRepository
from src.services.house_service import HouseService
from src.services.report_service import ReportService
from src.ui.menu import MainMenu
from src.utils.logger import logger


def main():
    try:
        logger.info("Запуск системи управління будинком...")
        resident_repo = ResidentRepository()
        apartment_repo = ApartmentRepository()
        residency_repo = ResidencyRepository()
        house_service = HouseService(
            resident_repo=resident_repo,
            apartment_repo=apartment_repo,
            residency_repo=residency_repo
        )

        report_service = ReportService(
            resident_repo=resident_repo,
            apartment_repo=apartment_repo
        )

        ui = MainMenu(
            house_service=house_service,
            report_service=report_service,
            resident_repo=resident_repo,
            apartment_repo=apartment_repo
        )

        ui.show_main_menu()

    except KeyboardInterrupt:
        print("\nПрограму перервано користувачем.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Критична помилка при запуску: {e}")
        print(f"Сталася непередбачувана помилка. Перевірте logs/app.log для деталей.")
        sys.exit(1)


if __name__ == "__main__":
    main()