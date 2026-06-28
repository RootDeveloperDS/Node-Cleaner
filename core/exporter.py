import csv
import json
from utils.logger import logger

def export_to_csv(data: list, file_path: str):
    if not data:
        return
    try:
        keys = data[0].keys()
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        logger.info(f"Exported {len(data)} items to CSV: {file_path}")
    except Exception as e:
        logger.error(f"Failed to export CSV to {file_path}: {e}")

def export_to_json(data: list, file_path: str):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logger.info(f"Exported {len(data)} items to JSON: {file_path}")
    except Exception as e:
        logger.error(f"Failed to export JSON to {file_path}: {e}")
