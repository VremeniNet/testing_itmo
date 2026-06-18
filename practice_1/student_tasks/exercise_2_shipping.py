"""
СТАРТОВЫЙ ФАЙЛ — Занятие 1, Challenge «Найди баг».

Задача:
    В модуле src/shipping.py есть НАМЕРЕННЫЙ дефект.
    Напишите тесты согласно спецификации — один из них упадёт.
    Опишите найденный баг в комментарии в конце файла.

Спецификация (краткая):
    Международная доставка:
        - до 1 кг: 500 руб.
        - 1–20 кг: 500 + 150 руб. за каждый кг сверх 1
        - > 20 кг: ValueError

Как запустить:
    pytest student_tasks/exercise_2_shipping.py -v
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from shipping import calculate_shipping


class TestInternationalShipping:
    """Международная доставка — здесь должен быть обнаружен баг."""

    def test_international_under_1kg(self):
        assert calculate_shipping(0.5, "international") == 500

    def test_international_exactly_1kg(self):
        assert calculate_shipping(1.0, "international") == 500

    def test_international_5kg(self):
        assert calculate_shipping(5.0, "international") == 1100

    def test_international_10kg(self):
        assert calculate_shipping(10.0, "international") == 1850

    def test_international_20kg(self):
        assert calculate_shipping(20.0, "international") == 3350

    def test_international_over_20kg(self):
        with pytest.raises(ValueError):
            calculate_shipping(20.1, "international")



# ════════════════════════════════════════════════════════════════
# ОПИСАНИЕ БАГА (заполнить после обнаружения)
# ════════════════════════════════════════════════════════════════
#
# В файле src/shipping.py в расчёте международной доставки используется
# неправильный тариф за каждый килограмм сверх 1 кг.
#
# По спецификации должно быть:
#     500 + 150 * (weight_kg - 1)
#
# В коде фактически используется:
#     500 + 100 * (weight_kg - 1)
#
# Из-за этого стоимость международной доставки для веса больше 1 кг
# получается меньше ожидаемой.
#
# Пример:
#     Для веса 5 кг ожидается:
#         500 + 150 * 4 = 1100
#
#     Фактически функция возвращает:
#         500 + 100 * 4 = 900
#
# Предлагаемое исправление:
#     заменить 100 на 150 в формуле расчёта международной доставки.
#
# ════════════════════════════════════════════════════════════════
