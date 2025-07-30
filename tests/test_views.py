import json
import os
from unittest.mock import Mock
import src.views as views


def test_home_page():
    date = "2025-01-01 04:59:59"

    mock_dummy = Mock(return_value="1")
    views.utils.get_greeting = mock_dummy
    os.path.abspath = mock_dummy
    views.utils.get_operations_from_excel = mock_dummy
    views.utils.get_operations_by_date = mock_dummy
    views.utils.get_payment_operations = mock_dummy
    views.utils.get_cards_data = mock_dummy
    mock_top = Mock(
        return_value=[
            {
                "Номер карты": "1234567812345678",
                "Статус": "OK",
                "Сумма операции": -1000,
                "Категория": "Супермаркеты",
                "Валюта операции": "RUB",
                "Дата платежа": "01.01.2025 12:00:00",
                "Описание": "Описание",
            }
        ]
    )
    views.utils.get_top_operations = mock_top
    views.utils.get_currencies_stocks = mock_dummy
    views.utils.get_currency_rates = mock_dummy
    views.utils.get_stock_prices = mock_dummy

    expected_result = {
        "greeting": "1",
        "cards": "1",
        "top_transactions": [
            {
                "date": "01.01.2025 12:00:00",
                "amount": -1000,
                "category": "Супермаркеты",
                "description": "Описание",
            }
        ],
        "currency_rates": "1",
        "stock_prices": "1",
    }
    expected_result = json.dumps(expected_result)

    assert views.home_page(date) == expected_result
