import logging
import os
import typing
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

import pandas as pd

logger = logging.getLogger("reports")
logger.setLevel(logging.DEBUG)
log_dir = os.path.abspath("../logs")
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(filename=f"{log_dir}/reports.log", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def report_saver(function: typing.Any = None, filename: Optional[str] = None) -> typing.Any:
    """
    Декоратор для сохранения результата функции-отчета в файл
    Если параметр filename не передан, создается файл с именем по умолчанию: 'report_YYYYMMDD_HHMMSS.csv'.
    :param function: Декорируемая функция
    :param filename: Путь к файлу
    :return: Результат работы функции
    """

    def decorator_report_saver(func: typing.Any) -> typing.Any:
        @wraps(func)
        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            result = func(*args, **kwargs)

            try:
                # Проверка имени файла
                if filename is None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename_to_use = f"report_{timestamp}.csv"
                    logger.info(f"Имя файла отчета не задано. Принимается имя: {filename_to_use}")
                else:
                    filename_to_use = filename
                    logger.info(f"Заданное имя файла отчета: {filename_to_use}")

                # Проверка на тип DataFrame
                if isinstance(result, pd.DataFrame):
                    result.to_csv(filename_to_use, index=False)
                    logger.info(f"Отчет сохранен в файл: {filename_to_use}")
                else:
                    with open(filename_to_use, "w", encoding="utf-8") as f_out:
                        f_out.write(str(result))
                    logger.info(f"Отчет сохранен как текст в файл: {filename_to_use}")
            except Exception as e:
                logger.error(f"Ошибка: {e}")
            finally:
                return result

        return wrapper

    # Вызов без параметра -> @report_saver
    if function is not None:
        return decorator_report_saver(function)
    # Вызов с параметром -> @report_saver(filename='my_report.csv')
    else:
        return decorator_report_saver


@report_saver
def spending_by_category(
    operations: pd.DataFrame, category: Optional[str], date: Optional[str] = None
) -> pd.DataFrame:
    """
    Функция возвращает траты по заданной категории за последние 3 месяца от заданной даты
    :param operations: Список транзакций (операций)
    :param category: Название категории
    :param date: Опциональная дата
    :return: Траты по заданной категории за последние три месяца (от переданной даты)
    """
    # Если дата не указана, берем текущую
    if date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")

    start_date = end_date - timedelta(days=90)
    logger.info(f"Начальная дата: {start_date}. Конечная дата: {end_date}")

    # Преобразуем колонку с датами в datetime
    operations["Дата операции datetime"] = pd.to_datetime(operations["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    # Фильтрация по категории и дате
    filtered = operations[
        (operations["Категория"] == category)
        & (operations["Дата операции datetime"] >= start_date)
        & (operations["Дата операции datetime"] <= end_date)
    ]
    logger.info("Операции отфильтрованы")

    # Группируем или суммируем траты
    total_spending = filtered[["Сумма платежа"]].sum().to_frame().T
    total_spending.insert(0, "Категория", category)
    total_spending.insert(1, "start_date", start_date.date())
    total_spending.insert(2, "end_date", end_date.date())
    logger.info("Траты сгруппированы и просуммированы")

    return total_spending
