import json
import logging
import os
from datetime import datetime, time
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
log_dir = Path(__file__).resolve().parent.parent / "logs"
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(filename=f"{log_dir}/utils.log", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_greeting(date: datetime) -> str:
    """
    Функция определяющее приветствие для текущего времени
    :param date: текущая дата и время
    :return: строка приветствия
    """
    try:
        logger.info("Определение приветствия успешно")
        if time(5, 0) <= date.time() < time(12, 0):
            return "Доброе утро"
        elif time(12, 0) <= date.time() < time(18, 0):
            return "Добрый день"
        elif time(18, 0) <= date.time() < time(23, 0):
            return "Добрый вечер"
        else:
            return "Доброй ночи"
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return ""


def get_operations_from_excel(filename: str = "") -> list[dict]:
    """
    Функция получения списка операций из файла excel
    :param filename: путь к файлу excel с данными операций
    :return: список операций
    """
    try:
        reader = pd.read_excel(filename)
        operations = reader.to_dict(orient="records")
        logger.info(f"Чтение excel-файла прошло успешно. Всего {len(operations)} значений")
        return operations
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return []


def get_operations_by_date(operations: list[dict], end_date: datetime) -> list[dict]:
    """
    Функция фильтрует операции по дате (со сначала месяца по текущую дату)
    :param operations: список операций
    :param end_date: конечная дата фильтрации
    :return: список операций по дате (со сначала месяца по текущую дату)
    """
    try:
        operations_by_date = []
        start_date = datetime(end_date.year, end_date.month, 1)
        for operation in operations:
            date_of_operation = datetime.strptime(operation["Дата операции"], "%d.%m.%Y %H:%M:%S")
            if start_date <= date_of_operation <= end_date:
                operations_by_date.append(operation)
        logger.info(
            f"Фильтрация операций по дате проведена ({start_date}-{end_date}).\
            Всего {len(operations_by_date)} значений"
        )
        return operations_by_date
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return []


def get_payment_operations(operations: list[dict]) -> list[dict]:
    """
    Функция для получения списка платежей из всех операций
    :param operations: список операций
    :return: список платежей из всех операций
    """
    try:
        payment_operations = [operation for operation in operations if operation["Статус"] == "OK"]
        payment_operations = [po for po in payment_operations if "Номер карты" in po]
        payment_operations = [po for po in payment_operations if po["Сумма операции"] < 0]
        payment_operations = [po for po in payment_operations if po["Категория"] != "Другое"]
        payment_operations = [po for po in payment_operations if po["Категория"] != "Бонусы"]
        payment_operations = [po for po in payment_operations if po["Категория"] != "Зарплата"]
        payment_operations = [po for po in payment_operations if po["Категория"] != "Переводы"]
        payment_operations = [po for po in payment_operations if po["Категория"] != "Пополнения"]
        logger.info(f"Поиск платежей проведен. Всего {len(payment_operations)} значений")

        return payment_operations
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return []


def get_cards_data(operations: list[dict]) -> list[dict]:
    """
    Функция формирует список карт с последними 4 цифрами, суммой расходов и кэшбэком
    :param operations: данные операций
    :return: список карт с последними 4 цифрами, суммой расходов и кэшбэком
    """
    try:
        cards_data = []

        card_numbers = set([op["Номер карты"] for op in operations])
        logger.info(f"Всего {len(card_numbers)} карт")

        for cn in card_numbers:
            last_digits = cn[-4:]
            total_spent = -sum(currency_conversions(op) for op in operations if op["Номер карты"] == cn)
            cashback = round(total_spent / 100, 2)
            cards_data.append({"last_digits": last_digits, "total_spent": total_spent, "cashback": cashback})

        return cards_data
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return []


def currency_conversions(operation: dict) -> Any:
    """
    Функция конвертации суммы операции в рубли
    :param operation: данные операции
    :return: сумма операции в рублях
    """
    try:
        amount = operation["Сумма операции"]
        currency = operation["Валюта операции"]
        date = datetime.strptime(operation["Дата операции"], "%d.%m.%Y %H:%M:%S")

        if currency == "RUB":
            logger.info(f"Платеж {amount} {currency}, перевод не требуется")
            return amount
        else:
            logger.info(f"Платеж {amount} {currency}, требуется перевод в RUB")
            url = "https://api.apilayer.com/exchangerates_data/convert"
            params = {"amount": abs(amount), "from": currency, "to": "RUB", "date": date.strftime("%Y-%m-%d")}
            load_dotenv()
            api_key = os.getenv("API_KEY")
            headers = {"apikey": api_key}

            response = requests.get(url, headers=headers, params=params)
            result = response.json()
            amount_rub = float(result["result"])
            logger.info(f"Платеж {amount_rub} RUB")
            return amount_rub
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return 0


def get_top_operations(operations: list[dict], n: int = 5) -> list[dict]:
    """
    Функция получения топа операций по сумме платежа
    :param operations: список операций
    :param n: количество выводимых операций
    :return: топ операций по сумме платежа
    """
    try:
        logger.info("Сортировка по убыванию суммы операции")
        sorted_operations = sorted(operations, key=lambda x: abs(x["Сумма операции"]), reverse=True)
        return sorted_operations[:n]
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return []


def get_currencies_stocks(filename: str = "") -> Any:
    """
    Функция чтения данных о пользовательских валютах и акциях
    :param filename: путь к файлу json
    :return: данные пользователя о валютах и акциях
    """
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            logger.info("Данные файла json считаны и загружены успешно")
            return data
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return {}


def get_currency_rates(currencies_stocks: dict) -> list[dict]:
    """
    Функция получения данных курсов пользовательских валют
    :param currencies_stocks: словарь со списком пользовательских валют
    :return: словарь с курсом валют
    """
    try:
        currencies = []
        logger.info("Получение информации о курсах валют")
        for currency in currencies_stocks["user_currencies"]:
            base_currency = currency
            target_currency = "RUB"
            url = f"https://api.apilayer.com/exchangerates_data/latest?base={base_currency}&symbols={target_currency}"
            load_dotenv()
            api_key = os.getenv("API_KEY")
            headers = {"apikey": api_key}
            response = requests.get(url, headers=headers)
            data = response.json()
            rate = data["rates"].get(target_currency)
            currencies.append({"currency": base_currency, "rate": rate})
            logger.info(f"1 {base_currency} = {rate} {target_currency}")
        return currencies
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return []


def get_stock_prices(currencies_stocks: dict) -> list[dict]:
    """
    Функция для получения текущих котировок акций
    :param currencies_stocks: словарь со списком тикеров акций
    :return: словарь с курсом акций
    """
    result = []
    try:
        tickers = currencies_stocks["user_stocks"]
        for ticker in tickers:
            stock = yf.Ticker(ticker)
            price = stock.history(period="1d")["Close"].iloc[-1]
            result.append({"stock": ticker, "price": float(round(price, 2))})
    except Exception as e:
        print(f"Ошибка: {e}")
    return result
