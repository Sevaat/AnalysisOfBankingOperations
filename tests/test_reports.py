import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.reports import report_saver, spending_by_category


def test_decorator_without_filename_dataframe():
    # Тест декоратора без имени файла с DataFrame
    with tempfile.TemporaryDirectory():

        @report_saver
        def test_func():
            return pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

        with patch("src.reports.datetime") as mock_datetime:
            mock_now = MagicMock()
            mock_now.strftime.return_value = "20230101_120000"
            mock_datetime.now.return_value = mock_now

            result = test_func()

            # Проверяем, что файл создался
            expected_filename = f'{Path(__file__).resolve().parent.parent / "reports"}/report_20230101_120000.csv'
            assert os.path.exists(expected_filename)

            # Проверяем содержимое файла
            saved_df = pd.read_csv(expected_filename)
            pd.testing.assert_frame_equal(result, saved_df)

            # Убираем файл
            os.remove(expected_filename)


def test_decorator_with_custom_filename_dataframe():
    # Тест декоратора с кастомным именем файла для DataFrame
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
        temp_filename = temp_file.name

    try:

        @report_saver(filename=temp_filename)
        def test_func():
            return pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

        result = test_func()

        # Проверяем, что файл создался
        assert os.path.exists(temp_filename)

        # Проверяем содержимое файла
        saved_df = pd.read_csv(temp_filename)
        pd.testing.assert_frame_equal(result, saved_df)

    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)


def test_decorator_without_filename_string():
    # Тест декоратора без имени файла с текстовым результатом
    with tempfile.TemporaryDirectory():
        test_text = "This is a test report"

        @report_saver
        def test_func():
            return test_text

        with patch("src.reports.datetime") as mock_datetime:
            mock_now = MagicMock()
            mock_now.strftime.return_value = "20230101_120000"
            mock_datetime.now.return_value = mock_now

            test_func()

            # Проверяем, что файл создался
            expected_filename = f'{Path(__file__).resolve().parent.parent / "reports"}/report_20230101_120000.csv'
            assert os.path.exists(expected_filename)

            # Проверяем содержимое файла
            with open(expected_filename, "r", encoding="utf-8") as f:
                content = f.read()
            assert content == test_text

            # Убираем файл
            os.remove(expected_filename)


def test_decorator_with_custom_filename_string():
    # Тест декоратора с кастомным именем файла для текста
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
        temp_filename = temp_file.name

    try:
        test_text = "This is a test report"

        @report_saver(filename=temp_filename)
        def test_func():
            return test_text

        test_func()

        # Проверяем, что файл создался
        assert os.path.exists(temp_filename)

        # Проверяем содержимое файла
        with open(temp_filename, "r", encoding="utf-8") as f:
            content = f.read()
        assert content == test_text

    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)


def test_decorator_preserves_function_metadata():
    # Тест, что декоратор сохраняет метаданные функции

    def original_func():
        """Original function docstring"""
        return "test"

    decorated_func = report_saver(original_func)

    assert decorated_func.__name__ == original_func.__name__
    assert decorated_func.__doc__ == original_func.__doc__


def test_decorator_returns_correct_result():
    # Тест, что декоратор возвращает правильный результат
    expected_result = pd.DataFrame({"test": [1, 2, 3]})

    @report_saver
    def test_func():
        return expected_result

    result = test_func()
    pd.testing.assert_frame_equal(result, expected_result)

    # Удаляем созданный файл
    filename = Path(__file__).resolve().parent.parent / "reports"
    date = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename}/report_{date}.csv"
    os.remove(filename)


def test_decorator_with_function_arguments():
    # Тест декоратора с аргументами функции
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
        temp_filename = temp_file.name

    try:

        @report_saver(filename=temp_filename)
        def test_func(x, y=2):
            return pd.DataFrame({"sum": [x + y], "product": [x * y]})

        result = test_func(3, y=4)

        assert os.path.exists(temp_filename)
        saved_df = pd.read_csv(temp_filename)
        pd.testing.assert_frame_equal(result, saved_df)

    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)


def test_decorator_with_none_result():
    # Тест декоратора с None результатом
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
        temp_filename = temp_file.name

    try:

        @report_saver(filename=temp_filename)
        def test_func():
            return None

        result = test_func()

        # Файл должен быть создан, но с пустым содержимым
        assert os.path.exists(temp_filename)
        assert result is None

    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)


def test_decorator_error_handling():
    # Тест обработки ошибок в декораторе
    # Создаем ситуацию, которая вызовет ошибку (попытка записи в несуществующую директорию)
    invalid_filename = "/non/existent/directory/report.csv"

    @report_saver(filename=invalid_filename)
    def test_func():
        return pd.DataFrame({"test": [1, 2, 3]})

    result = test_func()

    # Проверяем, что результат все равно возвращается
    assert isinstance(result, pd.DataFrame)


def test_basic_functionality(reports_sample_operations):
    # Тест базовой функциональности - правильный подсчет суммы
    result = spending_by_category(reports_sample_operations, "Продукты", "01.04.2023 00:00:00")

    # Проверяем структуру результата
    assert "Категория" in result.columns
    assert "start_date" in result.columns
    assert "end_date" in result.columns
    assert "Сумма платежа" in result.columns

    # Проверяем значения
    assert result["Категория"].iloc[0] == "Продукты"
    assert result["Сумма платежа"].iloc[0] == 4500  # 1000 + 2000 + 1500

    # Удаляем созданный файл
    filename = Path(__file__).resolve().parent.parent / "reports"
    date = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename}/report_{date}.csv"
    os.remove(filename)


def test_different_category(reports_sample_operations):
    # Тест для другой категории
    result = spending_by_category(reports_sample_operations, "Транспорт", "01.04.2023 00:00:00")

    assert result["Категория"].iloc[0] == "Транспорт"
    assert result["Сумма платежа"].iloc[0] == 500

    # Удаляем созданный файл
    filename = Path(__file__).resolve().parent.parent / "reports"
    date = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename}/report_{date}.csv"
    os.remove(filename)


def test_no_operations_in_period(reports_sample_operations):
    # Тест когда нет операций в указанном периоде
    result = spending_by_category(reports_sample_operations, "Развлечения", "01.04.2023 00:00:00")

    assert result["Категория"].iloc[0] == "Развлечения"
    assert result["Сумма платежа"].iloc[0] == 0

    # Удаляем созданный файл
    filename = Path(__file__).resolve().parent.parent / "reports"
    date = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename}/report_{date}.csv"
    os.remove(filename)


def test_empty_dataframe():
    # Тест с пустым DataFrame
    empty_data = pd.DataFrame(columns=["Дата операции", "Категория", "Сумма платежа"])
    result = spending_by_category(empty_data, "Продукты", "01.04.2023 00:00:00")

    assert result["Категория"].iloc[0] == "Продукты"
    assert result["Сумма платежа"].iloc[0] == 0

    # Удаляем созданный файл
    filename = Path(__file__).resolve().parent.parent / "reports"
    date = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename}/report_{date}.csv"
    os.remove(filename)


def test_edge_case_exact_dates():
    # Тест пограничных случаев с точными датами
    # Создаем данные с операциями точно на границах периода
    edge_data = pd.DataFrame(
        {
            "Дата операции": [
                "01.01.2023 23:59:59",  # Начало периода (90 дней от 01.04.2023)
                "01.04.2023 23:59:59",  # Конец периода
                "31.12.2022 23:59:59",  # За пределами периода
                "02.04.2023 00:00:00",  # За пределами периода
            ],
            "Категория": ["Продукты", "Продукты", "Продукты", "Продукты"],
            "Сумма платежа": [100, 200, 300, 400],
        }
    )

    result = spending_by_category(edge_data, "Продукты", "01.04.2023 23:59:59")

    # Должны войти только первые две операции
    assert result["Сумма платежа"].iloc[0] == 300

    # Удаляем созданный файл
    filename = Path(__file__).resolve().parent.parent / "reports"
    date = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename}/report_{date}.csv"
    os.remove(filename)


def test_invalid_date_format(reports_sample_operations):
    # Тест с некорректным форматом даты
    with pytest.raises(ValueError):
        spending_by_category(reports_sample_operations, "Продукты", "2023-04-01 00:00:00")

    # Удаляем созданный файл
    files = [f for f in os.listdir(".") if f.startswith("report_") and f.endswith(".csv")]
    for file in files:
        os.remove(file)
