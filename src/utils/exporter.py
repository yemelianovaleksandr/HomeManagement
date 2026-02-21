import csv
import json
import os
from datetime import datetime
from src.utils.logger import logger


class Exporter:
    OUTPUT_DIR = "data/output"

    @classmethod
    def _prepare_directory(cls):
        # Перевіряє наявність папки для звітів
        if not os.path.exists(cls.OUTPUT_DIR):
            os.makedirs(cls.OUTPUT_DIR)
            logger.info(f"Створено директорію для експорту: {cls.OUTPUT_DIR}")

    @classmethod
    def to_csv(cls, data, filename_prefix, headers):
        cls._prepare_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(cls.OUTPUT_DIR, f"{filename_prefix}_{timestamp}.csv")

        try:
            with open(filepath, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(headers)
                writer.writerows(data)

            logger.info(f"Звіт успішно експортовано в CSV: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Помилка при експорті в CSV: {e}")
            raise

    @classmethod
    def to_json(cls, data, filename_prefix):
        cls._prepare_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(cls.OUTPUT_DIR, f"{filename_prefix}_{timestamp}.json")

        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False, default=str)

            logger.info(f"Звіт успішно експортовано в JSON: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Помилка при експорті в JSON: {e}")
            raise