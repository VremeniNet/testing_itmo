"""
СТАРТОВЫЙ ФАЙЛ — Занятие 1, Упражнение 1.

Задача: дописать тесты для функции assign_grade из src/grading.py.
Эталонное решение: tests/unit/test_grading.py

Как запустить:
    pytest student_tasks/exercise_1_grading.py -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from grading import assign_grade


class TestAssignGradePositive:
    """Позитивные сценарии: середины классов эквивалентности."""

    def test_score_20_returns_F(self):
        assert assign_grade(20) == "F"

    def test_score_50_returns_D(self):
        assert assign_grade(50) == "D"

    def test_score_67_returns_C(self):
        assert assign_grade(67) == "C"

    def test_score_82_returns_B(self):
        assert assign_grade(82) == "B"

    def test_score_95_returns_A(self):
        assert assign_grade(95) == "A"


class TestAssignGradeBoundary:
    """Граничные значения на стыках классов."""

    def test_score_0_returns_F(self):
        assert assign_grade(0) == "F"

    def test_score_39_returns_F(self):
        assert assign_grade(39) == "F"

    def test_score_40_returns_D(self):
        assert assign_grade(40) == "D"

    def test_score_59_returns_D(self):
        assert assign_grade(59) == "D"

    def test_score_60_returns_C(self):
        assert assign_grade(60) == "C"

    def test_score_74_returns_C(self):
        assert assign_grade(74) == "C"

    def test_score_75_returns_B(self):
        assert assign_grade(75) == "B"

    def test_score_89_returns_B(self):
        assert assign_grade(89) == "B"

    def test_score_90_returns_A(self):
        assert assign_grade(90) == "A"

    def test_score_100_returns_A(self):
        assert assign_grade(100) == "A"


class TestAssignGradeNegative:
    """Негативные сценарии."""

    def test_negative_score_raises_value_error(self):
        with pytest.raises(ValueError):
            assign_grade(-1)

    def test_score_over_100_raises_value_error(self):
        with pytest.raises(ValueError):
            assign_grade(101)

    def test_float_score_raises_type_error(self):
        with pytest.raises(TypeError):
            assign_grade(85.5)

    def test_string_score_raises_type_error(self):
        with pytest.raises(TypeError):
            assign_grade("90")


class TestAssignGradeOlympiad:
    """Олимпиадный бонус +1 к оценке."""

    def test_olympiad_F_becomes_D(self):
        assert assign_grade(20, is_olympiad_winner=True) == "D"

    def test_olympiad_D_becomes_C(self):
        assert assign_grade(50, is_olympiad_winner=True) == "C"

    def test_olympiad_C_becomes_B(self):
        assert assign_grade(67, is_olympiad_winner=True) == "B"

    def test_olympiad_B_becomes_A(self):
        assert assign_grade(82, is_olympiad_winner=True) == "A"

    def test_olympiad_A_stays_A(self):
        assert assign_grade(95, is_olympiad_winner=True) == "A"
