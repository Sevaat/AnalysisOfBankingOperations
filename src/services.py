import json
import logging
import os

logger = logging.getLogger("services")
logger.setLevel(logging.DEBUG)
log_dir = os.path.abspath("../logs")
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(filename=f"{log_dir}/services.log", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def simple_search(operations: list[dict], search_query: str) -> str:
    """
    Функция для фильтрации транзакций по строке поиска в описании или категории

    :param operations: список словарей с данными операций
    :param search_query: строка для поиска
    :return: json-строка с отфильтрованными операциями
    """
    try:
        if not search_query:
            logger.info(f"Для поиска ничего не передано. Возвращены все {len(operations)} операции")
            return json.dumps(operations)

        operations_found = []
        for op in operations:
            if "Категория" in op:
                if search_query.lower() in op["Категория"].lower():
                    operations_found.append(op)
            if "Описание" in op:
                if search_query.lower() in op["Описание"].lower() and op not in operations_found:
                    operations_found.append(op)

        logger.info(f"Возвращены {len(operations_found)} операции по ключу {search_query}")
        return json.dumps(operations_found)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return json.dumps(operations)
