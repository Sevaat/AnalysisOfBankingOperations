
# Курсовой проект: AnalysisOfBankingOperations

Приложение для анализа транзакций, которые находятся в Excel-файле. Приложение будет генерировать JSON-данные для веб-страниц, формировать Excel-отчеты, а также предоставлять другие сервисы.


## Благодарности

Благодарность ОАНО ДПО "СКАЕНГ".
## Справка по API

#### Курс валют

https://apilayer.com/marketplace/exchangerates_data-api

#### Курс акций

https://ranaroussi.github.io/yfinance/


## Авторы

tkachenko <sevaatmail@mail.com>


## Установка

Работа программы производится при запуске файла main.py, хранящегося в корне проекта.
    
## Выполнение тестов

В проекте использована библиотека pytest. Запуск тестов производится командой в терминале pytest.


## Использование/Примеры

#### Функция определяющее приветствие для текущего времени

greeting = utils.get_greeting(date)

#### Функция получения списка операций из файла excel

operations = utils.get_operations_from_excel(filename)

#### Функция фильтрует операции по дате (со сначала месяца по текущую дату)

operations = utils.get_operations_by_date(operations, date)

#### Функция для получения списка платежей из всех операций

operations = utils.get_payment_operations(operations)

#### Функция формирует список карт с последними 4 цифрами, суммой расходов и кэшбэком

cards_data = utils.get_cards_data(operations)

#### Функция получения топа операций по сумме платежа

top_operations = utils.get_top_operations(operations)

#### Функция получения данных курсов пользовательских валют

currencies = utils.get_currency_rates(currencies_stocks)

#### Функция для получения текущих котировок акций

stocks = utils.get_stock_prices(currencies_stocks)

#### Функция для фильтрации транзакций по строке поиска в описании или категории

operations = simple_search(operations, search_query)

#### Функция возвращает траты по заданной категории за последние 3 месяца от заданной даты

total_spending = spending_by_category(df_operations, category, date)