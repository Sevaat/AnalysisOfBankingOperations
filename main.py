from pathlib import Path

import pandas as pd

from src.reports import spending_by_category
from src.services import simple_search
from src.utils import get_operations_from_excel
from src.views import home_page


def main():
    # Наполняем главную страницу содержимым
    print('Введите дату в формате "ГГ-ММ-ДД ЧЧ:ММ:СС":')
    date = input()
    json_home_page = home_page(date)
    print("Содержимое главной страницы сформировано...")
    print(json_home_page)

    # Проверяем работу сервисов
    filename_excel = Path(__file__).resolve().parent.parent / "data"
    filename_excel = f"{filename_excel}/operations.xlsx"
    operations = get_operations_from_excel(filename_excel)
    print("Введите запрос для поиска в описании или категории:")
    search_query = input()
    operations_found = simple_search(operations, search_query)
    print("Операции по описанию или категории найдены...")
    print(operations_found)

    # Проверяем работу отчетов
    df_operations = pd.DataFrame(operations)
    print("Введите необходимую категорию:")
    category = input()
    print("Введите необходимую дату (если дата пустая, то будет выбрана текущая дата):")
    date = input()
    if date != "":
        total_spending = spending_by_category(df_operations, category, date)
    else:
        total_spending = spending_by_category(df_operations, category)
    print("Траты по категории за последние 3 месяца сформированы...")
    print(total_spending)


if __name__ == "__main__":
    main()
