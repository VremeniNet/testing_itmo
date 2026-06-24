# Практическая работа 3

Дисциплина: **Тестирование**

Выполнил: студент **Желанов Даниил**

Группа: **P4150**

## Описание

В данной практической работе рассматриваются BDD-тестирование, Gherkin-сценарии, property-based testing и основы мутационного тестирования.

Проект представляет собой домен пиццерии: каталог пицц, заказ, расчёт стоимости, скидки, доставка и управление статусами заказа.

В работе используются:

* `pytest`;
* `pytest-bdd`;
* Gherkin-сценарии на русском языке;
* шаги `given`, `when`, `then`;
* `Hypothesis`;
* стратегии генерации данных;
* `assume()`;
* property-based тесты;
* мутационное тестирование через `cosmic-ray`.

## Структура

```text
practice_3/
├── src/
│   └── pizza_service/
├── tests/
├── student_tasks/
│   ├── exercise_property_based.py
│   ├── features/
│   │   └── order_management.feature
│   └── step_defs/
│       └── test_order_management.py
├── pytest.ini
├── requirements.txt
├── cosmic-ray.toml
├── cosmic-ray-weak.toml
└── README.md
```

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Задание 1. BDD и Gherkin

Файлы:

```text
student_tasks/features/order_management.feature
student_tasks/step_defs/test_order_management.py
```

Были реализованы BDD-сценарии для управления заказом:

* клиент удаляет позицию из заказа;
* клиент отменяет подтверждённый заказ;
* система запрещает изменение подтверждённого заказа.

Команда запуска:

```bash
python -m pytest student_tasks/step_defs/test_order_management.py -v
```

Ожидаемый результат:

```text
3 passed
```

## Задание 2. Property-based testing

Файл:

```text
student_tasks/exercise_property_based.py
```

Были реализованы property-based тесты для домена пиццерии.

Проверяются свойства:

* промокод не увеличивает итоговую сумму в случаях, где скидка не меняет условие бесплатной доставки;
* итоговая сумма непустого заказа всегда положительна;
* при достижении порога бесплатной доставки доставка не добавляется;
* удаление позиции уменьшает сумму заказа без скидок.

Команда запуска:

```bash
python -m pytest student_tasks/exercise_property_based.py -v
```

Ожидаемый результат:

```text
4 passed
```

Команда запуска со статистикой Hypothesis:

```bash
python -m pytest student_tasks/exercise_property_based.py --hypothesis-show-statistics
```

## Мутационное тестирование

В проекте есть конфигурации для `cosmic-ray`:

```text
cosmic-ray.toml
cosmic-ray-weak.toml
```

Пример запуска мутационного тестирования:

```bash
cosmic-ray init cosmic-ray-weak.toml weak.sqlite
cosmic-ray exec cosmic-ray-weak.toml weak.sqlite
cr-report weak.sqlite
```

Слабые тесты из `tests/property_weak/` используются для демонстрации выживших мутантов.

## Общие команды

Запуск эталонных тестов проекта:

```bash
python -m pytest tests/ -v
```

Запуск BDD-задания студента:

```bash
python -m pytest student_tasks/step_defs/test_order_management.py -v
```

Запуск property-based задания студента:

```bash
python -m pytest student_tasks/exercise_property_based.py -v
```

Важно: команда `python -m pytest student_tasks/ -v` запускает только файлы, подходящие под шаблон `test_*.py`, поэтому property-based файл `exercise_property_based.py` лучше запускать явно.

## Вывод

В ходе практической работы были написаны BDD-сценарии на русском языке и реализованы шаги для них через `pytest-bdd`.

Также были написаны property-based тесты с использованием `Hypothesis`, которые проверяют инварианты предметной области на множестве сгенерированных данных.
