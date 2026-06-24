# Практическая работа 4

Дисциплина: **Тестирование**

Выполнил: студент **Желанов Даниил**

Группа: **P4150**

## Описание

В данной практической работе выполнено тестирование проекта интернет-магазина книг.

Проверялись:

* бизнес-логика расчёта стоимости заказа;
* оформление заказа с внешними зависимостями;
* HTTP API;
* свойства расчёта стоимости через property-based тесты;
* устойчивость тестов через мутационное тестирование.

## Структура

```text
practice_4/
├── src/
│   └── bookstore/
├── tests/
│   ├── unit/
│   │   └── test_pricing.py
│   ├── mocks/
│   │   └── test_order_service_checkout.py
│   ├── api/
│   │   └── test_api.py
│   └── property/
│       └── test_pricing_properties.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Unit-тесты

Файл:

```text
tests/unit/test_pricing.py
```

Проверяется сервис `PricingService`: скидки, промокоды, доставка, НДС, коллекционные книги и невалидные заказы.

Команда запуска:

```bash
python -m pytest tests/unit/test_pricing.py -v
```

Результат:

```text
14 passed
```

## Тесты с моками

Файл:

```text
tests/mocks/test_order_service_checkout.py
```

Проверяется метод `OrderService.checkout` с использованием `MagicMock`.

Проверены сценарии успешного оформления заказа, ошибок резервирования, ошибок оплаты и ошибок отправки уведомлений.

Команда запуска:

```bash
python -m pytest tests/mocks/test_order_service_checkout.py -v
```

Результат:

```text
6 passed
```

## API-тесты

Файл:

```text
tests/api/test_api.py
```

Проверяется FastAPI-приложение через `TestClient`.

Проверены создание заказа, ошибки валидации, ошибки checkout и успешное оформление заказа.

Команда запуска:

```bash
python -m pytest tests/api/test_api.py -v
```

Результат:

```text
9 passed
```


## Property-based тесты

Файл:

```text
tests/property/test_pricing_properties.py
```

С помощью `Hypothesis` проверяются свойства расчёта стоимости:

* итоговая сумма равна сумме компонентов;
* НДС равен 10% от суммы после скидки;
* детские книги всегда дают бесплатную доставку;
* коллекционные книги не получают скидку;
* доставка для лёгкого заказа не меньше базовой стоимости.

Команда запуска:

```bash
python -m pytest tests/property/test_pricing_properties.py -v
```

Результат:

```text
5 passed
```

## Общий запуск тестов

```bash
python -m pytest tests -v
```

Результат:

```text
34 passed
```

## Мутационное тестирование

Для мутационного тестирования используется `cosmic-ray`.

Объект проверки:

```text
src/bookstore/pricing.py
```

Конфигурация:

```text
cosmic-ray.toml
```

Команды запуска:

```bash
python -m pytest -q
cosmic-ray init cosmic-ray.toml mutation-session.sqlite --force
cosmic-ray exec cosmic-ray.toml mutation-session.sqlite
cr-report mutation-session.sqlite
```

Результат запуска:

```text
total jobs: 238
complete: 238 (100.00%)
surviving mutants: 34 (14.29%)
```

Мутационное тестирование показало, что большая часть изменений в `PricingService` обнаруживается тестами. Выжившие мутанты показывают места, где поведение либо не изменяется заметным образом, либо может требовать дополнительных проверок.

## Вывод

В ходе работы были написаны unit-тесты, тесты с моками, API-тесты и property-based тесты.

Все обычные тесты проходят успешно:

```text
34 passed
```

Также было выполнено мутационное тестирование модуля `PricingService`.
