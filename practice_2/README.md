# Практическая работа 2

Дисциплина: **Тестирование**

Выполнил: студент **Желанов Даниил**
Группа: **P4150**

## Описание

В данной практической работе рассматривается тестирование REST API и использование моков при тестировании сервисного слоя.

Проект представляет собой FastAPI-приложение для работы с биржевыми календарями и торговыми датами.

В работе используются:

* `pytest`;
* `unittest.mock.MagicMock`;
* `side_effect`;
* `return_value`;
* `assert_called_once_with`;
* `assert_not_called`;
* `FastAPI TestClient`;
* `dependency_overrides`;
* параметризация тестов;
* проверка HTTP-статусов;
* проверка валидации Pydantic.

## Структура

```text
practice_2/
├── src/
│   └── trading_api/
├── tests/
├── student_tasks/
│   ├── exercise_4_mocks.py
│   └── exercise_5_api.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Упражнение 4. Моки

Файл:

```text
student_tasks/exercise_4_mocks.py
```

В упражнении написаны тесты для `SettlementService`.

Проверены следующие сценарии:

* базовый расчёт settlement-инструкции;
* корректный вызов внешнего провайдера курсов;
* использование `side_effect` как функции;
* проброс `LookupError`;
* проброс `ConnectionError`;
* отсутствие вызова провайдера при невалидной сумме.

Команда запуска:

```bash
python -m pytest student_tasks/exercise_4_mocks.py -v
```

Результат:

```text
6 passed
```

## Упражнение 5. API-тесты

Файл:

```text
student_tasks/exercise_5_api.py
```

В упражнении написаны тесты для FastAPI-приложения через `TestClient`.

Проверены следующие сценарии:

* получение списка бирж;
* наличие биржи `MOEX` в списке;
* получение статуса биржи с подменой текущего времени;
* обработка неизвестной биржи;
* расчёт торговых дней через `POST /trading-days/add`;
* параметризованные сценарии для разных бирж и дат;
* ошибка валидации при слишком большом количестве дней;
* ошибка валидации при отсутствии обязательного поля.

Команда запуска:

```bash
python -m pytest student_tasks/exercise_5_api.py -v
```

Результат:

```text
10 passed
```

## Общие команды

Запуск всех тестов проекта:

```bash
python -m pytest
```

Запуск только заданий студента:

```bash
python -m pytest student_tasks/ -v
```

Запуск тестов с покрытием:

```bash
python -m pytest --cov=src --cov-branch --cov-report=term-missing
```

## Вывод

В ходе практической работы были написаны тесты для сервисного слоя с использованием моков и тесты для REST API через FastAPI `TestClient`.

Моки позволяют изолировать тестируемый код от внешних зависимостей, а `TestClient` позволяет проверять API без запуска отдельного HTTP-сервера.
