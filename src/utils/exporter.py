import csv
import json
import os



class Exporter:

    @staticmethod
    def _prepare_directory(directory="exports"):
        # Створює папку, якщо її ще немає
        if not os.path.exists(directory):
            os.makedirs(directory)
        return directory

    @staticmethod
    def to_json(data, filename):
        folder = Exporter._prepare_directory()
        path = os.path.join(folder, f"{filename}.json")

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return path

    @staticmethod
    def to_csv(data, filename, headers=None):
        folder = Exporter._prepare_directory()
        path = os.path.join(folder, f"{filename}.csv")

        with open(path, 'w', newline='', encoding='utf-8') as f:
            if data and isinstance(data[0], dict):
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            else:
                writer = csv.writer(f)
                if headers:
                    writer.writerow(headers)
                writer.writerows(data)
        return path