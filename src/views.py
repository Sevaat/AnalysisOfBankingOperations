import json
import logging
import os
from datetime import datetime
from pathlib import Path

import src.utils as utils

logger = logging.getLogger("views")
logger.setLevel(logging.DEBUG)
log_dir = Path(__file__).resolve().parent.parent / "logs"
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(filename=f"{log_dir}/views.log", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def home_page(input_date: str) -> str:
    """
    Функция для наполнения главной страницы через json
    :param input_date: входящая дата для фильтрации данных
    :return: json-ответ
    """
    try:
        date = datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        return json.dumps({"error": "Неверный формат даты-времени"})

    # форма приветствия
    greeting = utils.get_greeting(date)
    # чтение excel
    filename = Path(__file__).resolve().parent.parent / "data"
    filename = f"{filename}/operations.xlsx"
    operations = utils.get_operations_from_excel(filename)
    # сортировка по дате
    operations = utils.get_operations_by_date(operations, date)
    # фильтрация по платежам
    operations = utils.get_payment_operations(operations)
    # данные карт
    cards_data = utils.get_cards_data(operations)
    # получение топа платежных операций
    top_operations = utils.get_top_operations(operations)
    top = []
    try:
        for to in top_operations:
            top.append(
                {
                    "date": to["Дата платежа"],
                    "amount": to["Сумма операции"],
                    "category": to["Категория"],
                    "description": to["Описание"],
                }
            )
    except Exception as e:
        logging.error(f"Ошибка: {e}")
    # получение пользовательских валют и акций
    filename = Path(__file__).resolve().parent.parent
    filename = f"{filename}/user_settings.json"
    currencies_stocks = utils.get_currencies_stocks(filename)
    # получение курса валют
    currencies = utils.get_currency_rates(currencies_stocks)
    # получение курса акций
    stocks = utils.get_stock_prices(currencies_stocks)

    result = {
        "greeting": greeting,
        "cards": cards_data,
        "top_transactions": top,
        "currency_rates": currencies,
        "stock_prices": stocks,
    }
    return json.dumps(result)
