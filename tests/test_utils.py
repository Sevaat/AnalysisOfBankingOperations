import json
from datetime import datetime
from unittest.mock import MagicMock, Mock, mock_open, patch

import pandas
import pytest
import requests

import src.utils as utils


@pytest.mark.parametrize(
    "date, result",
    [
        ([2025, 1, 1, 5, 0], "Доброе утро"),
        ([2025, 1, 1, 8, 30], "Доброе утро"),
        ([2025, 1, 1, 11, 59, 59], "Доброе утро"),
        ([2025, 1, 1, 12, 0], "Добрый день"),
        ([2025, 1, 1, 15, 30], "Добрый день"),
        ([2025, 1, 1, 17, 59, 59], "Добрый день"),
        ([2025, 1, 1, 18, 0], "Добрый вечер"),
        ([2025, 1, 1, 20, 30], "Добрый вечер"),
        ([2025, 1, 1, 22, 59, 59], "Добрый вечер"),
        ([2025, 1, 1, 23, 0], "Доброй ночи"),
        ([2025, 1, 1, 2, 30], "Доброй ночи"),
        ([2025, 1, 1, 4, 59, 59], "Доброй ночи"),
    ],
)
def test_get_greeting(date, result):
    now_date = datetime(date[0], date[1], date[2], date[3], date[4])
    assert utils.get_greeting(now_date) == result


def test_get_operations_from_excel():
    # корректное чтение
    test_data = pandas.DataFrame([{"a": 1, "b": 2}, {"a": 3, "b": 4}])
    with patch("pandas.read_excel", return_value=test_data):
        result = utils.get_operations_from_excel("valid.xlsx")
        assert result == [{"a": 1, "b": 2}, {"a": 3, "b": 4}]

    # пустой excel
    test_data = pandas.DataFrame()
    with patch("pandas.read_excel", return_value=test_data):
        result = utils.get_operations_from_excel("empty.xlsx")
        assert result == []

    # пустые данные в excel
    with patch("pandas.read_excel", side_effect=pandas.errors.EmptyDataError()):
        result = utils.get_operations_from_excel("empty_data.xlsx")
        assert result == []

    # несуществующий файл
    with patch("pandas.read_excel", side_effect=FileNotFoundError):
        result = utils.get_operations_from_excel("nonexistent.xlsx")
        assert result == []

    # неверный формат файла
    with patch("pandas.read_excel", side_effect=ValueError("Invalid file")):
        result = utils.get_operations_from_excel("invalid.txt")
        assert result == []

    # проверка на выброс исключения
    with patch("pandas.read_excel", side_effect=Exception("Any error")):
        result = utils.get_operations_from_excel("error.xlsx")
        assert result == []

    # пустое имя файла
    assert utils.get_operations_from_excel("") == []


def test_get_operations_by_date(operations_with_dates):
    # корректная работа
    end_date = datetime(2025, 5, 31)
    result = utils.get_operations_by_date(operations_with_dates, end_date)
    assert len(result) == 2
    assert {"Дата операции": "01.05.2025 00:00:00", "Сумма": 100} in result
    assert {"Дата операции": "15.05.2025 00:00:00", "Сумма": 200} in result

    # пустой список
    result = utils.get_operations_by_date([], end_date)
    assert result == []

    # нет подходящих операций
    result = utils.get_operations_by_date(operations_with_dates, datetime(2024, 5, 31))
    assert result == []

    # некорректная дата
    test_operations = [{"Дата операции": "invalid-date", "Сумма": 100}]
    assert utils.get_operations_by_date(test_operations, datetime(2023, 5, 31)) == []


def test_get_payment_operations(payment_operations):
    # корректная работа
    result = utils.get_payment_operations(payment_operations)
    assert len(result) == 3
    assert {
        "Номер карты": "1234567812345678",
        "Статус": "OK",
        "Сумма операции": -1000,
        "Категория": "Супермаркеты",
        "Валюта операции": "RUB",
        "Дата операции": "01.01.2025 12:00:00",
    } in result
    assert {
        "Номер карты": "1234567812345678",
        "Статус": "OK",
        "Сумма операции": -2000,
        "Категория": "Рестораны",
        "Валюта операции": "RUB",
        "Дата операции": "01.01.2025 12:00:00",
    } in result
    assert {
        "Номер карты": "8765432187654321",
        "Статус": "OK",
        "Сумма операции": -1500,
        "Категория": "Транспорт",
        "Валюта операции": "RUB",
        "Дата операции": "01.01.2025 12:00:00",
    } in result

    # пустой список операций
    assert utils.get_payment_operations([]) == []

    # нет подходящих операций
    assert utils.get_payment_operations(payment_operations[-3:]) == []

    # тест обработки исключений
    assert utils.get_payment_operations([{"invalid": "data"}]) == []


def test_get_cards_data(cards_data):
    # корректная работа
    result = utils.get_cards_data(cards_data)
    assert len(result) == 2
    assert {"last_digits": "5678", "total_spent": 3000, "cashback": 30.0} in result
    assert {"last_digits": "4321", "total_spent": 1500, "cashback": 15.0} in result

    # пустой список операций
    assert utils.get_cards_data([]) == []

    # тест обработки исключений
    assert utils.get_cards_data([{"invalid": "data"}]) == []


def test_currency_conversions():
    # без конвертации (RUB)
    operation = {"Сумма операции": -1000.0, "Валюта операции": "RUB", "Дата операции": "01.01.2025 12:00:00"}
    result = utils.currency_conversions(operation)
    assert result == -1000.0

    # успешная конвертация
    mock_data = {"Сумма операции": 100, "Валюта операции": "USD", "Дата операции": "01.01.2025 12:00:00"}
    json_str = '{"result": 7500}'
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.text = json_str
    mock_response.json.return_value = eval(json_str)

    with patch("requests.get", return_value=mock_response):
        result = utils.currency_conversions(mock_data)
        assert result == 7500

    # тест обработки исключений
    assert utils.currency_conversions({"invalid": "data"}) == 0


def test_get_top_operations(payment_operations):
    # корректная работа
    result = utils.get_top_operations(payment_operations, 2)
    assert result[0]["Сумма операции"] == -2000
    assert result[1]["Сумма операции"] == -1500

    # пустой список
    result = utils.get_top_operations([])
    assert result == []

    # значений списка мало
    result = utils.get_top_operations(payment_operations, 10)
    assert len(result) == 7
    assert result[0]["Сумма операции"] == -2000
    assert result[1]["Сумма операции"] == -1500

    # обработка исключений
    test_data = [{"Сумма операции": 100}, {"Описание": "Без суммы"}]
    result = utils.get_top_operations(test_data)
    assert result == []


def test_get_currencies_stocks():
    # корректная работа
    mock_data = {"currencies": ["USD", "EUR"], "stocks": ["AAPL", "GOOG"]}
    mock_json = json.dumps(mock_data)
    with patch("builtins.open", mock_open(read_data=mock_json)):
        result = utils.get_currencies_stocks("dummy_path.json")
    assert result == mock_data

    # проверка на ошибку в чтении json
    with patch("builtins.open", mock_open(read_data="invalid json")):
        with patch("json.load", side_effect=json.JSONDecodeError("Error", "doc", 0)):
            result = utils.get_currencies_stocks("invalid.json")
    assert result == {}

    # проверка на отсутствие файла
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = utils.get_currencies_stocks("nonexistent.json")
    assert result == {}


def test_get_currency_rates(
    monkeypatch, user_currencies_stocks, fake_env_api_key, fake_response_usd, fake_response_eur
):
    # корректная работа
    with patch("requests.get") as mock_get:
        mock_get.side_effect = [fake_response_usd, fake_response_eur]
        from src.utils import get_currency_rates

        result = get_currency_rates(user_currencies_stocks)
        assert result == [
            {"currency": "USD", "rate": 100.0},
            {"currency": "EUR", "rate": 110.0},
        ]
        assert mock_get.call_args_list[0][1]["headers"]["apikey"] == "test_api_key"
        assert mock_get.call_args_list[1][1]["headers"]["apikey"] == "test_api_key"

    # ошибка при запросе
    monkeypatch.setenv("API_KEY", "test_api_key")
    with patch("requests.get", side_effect=Exception("Network error")):
        from src.utils import get_currency_rates

        result = get_currency_rates(user_currencies_stocks)
        assert result == []

    # отсутствуют рубли
    monkeypatch.setenv("API_KEY", "test_api_key")
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"rates": {}}
    with patch("requests.get", return_value=mock_resp):
        from src.utils import get_currency_rates

        result = get_currency_rates(user_currencies_stocks)
        assert result == [
            {"currency": "USD", "rate": None},
            {"currency": "EUR", "rate": None},
        ]
