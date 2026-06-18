"""
ДОМАШНЕЕ ЗАДАНИЕ — после Занятия 2.

Задача:
    Написать полный набор тестов для корзины покупок (src/cart.py).
    Требования:
        - Использовать фикстуры (минимум 3)
        - Применить параметризацию (хотя бы для промокодов)
        - Разметить тесты маркерами smoke/boundary/negative
        - Добиться покрытия ≥ 95%
        - Минимум 15 тест-кейсов

Эталон: tests/unit/test_cart.py

Как проверить:
    pytest student_tasks/homework_cart.py -v
    pytest student_tasks/homework_cart.py --cov=src.cart --cov-report=term-missing

Критерии оценки:
    [ ] ≥ 15 тест-кейсов
    [ ] ≥ 3 фикстуры (пустая корзина, корзина с товарами, товары)
    [ ] Параметризация для промокодов SAVE10/SAVE20/HALF
    [ ] Маркеры smoke, boundary, negative использованы
    [ ] Покрытие ≥ 95% (branch coverage)
    [ ] Все тесты проходят
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from cart import Cart, Product


# ══════════════════════════════════════════════════════════════
#  ФИКСТУРЫ (3+)
# ══════════════════════════════════════════════════════════════


@pytest.fixture
def product_book():
    """Товар 'Книга' — 500 руб., 10 на складе."""
    return Product(name="Книга", price=500.0, stock=10)

@pytest.fixture
def product_pen():
    return Product(name="Ручка", price=50.0, stock=100)


@pytest.fixture
def product_laptop():
    return Product(name="Ноутбук", price=75000.0, stock=2)


@pytest.fixture
def empty_cart():
    return Cart()


@pytest.fixture
def cart_with_items(empty_cart, product_book, product_pen):
    empty_cart.add(product_book, 2)
    empty_cart.add(product_pen, 3)
    return empty_cart



# ══════════════════════════════════════════════════════════════
#  ТЕСТЫ
# ══════════════════════════════════════════════════════════════


class TestCartAdd:
    """Добавление товаров."""

    @pytest.mark.smoke
    def test_add_single_item(self, empty_cart, product_book):
        empty_cart.add(product_book)

        assert empty_cart.get_item_count() == 1
        assert empty_cart.is_empty() is False
        assert empty_cart.get_total() == 500.0

    def test_add_multiple_units(self, empty_cart, product_book):
        empty_cart.add(product_book, quantity=5)

        assert empty_cart.get_item_count() == 5
        assert empty_cart.get_total() == 2500.0

    def test_add_same_product_twice(self, empty_cart, product_book):
        empty_cart.add(product_book, 2)
        empty_cart.add(product_book, 3)

        assert empty_cart.get_item_count() == 5
        assert empty_cart.get_total() == 2500.0

    def test_add_different_products(self, empty_cart, product_book, product_pen):
        empty_cart.add(product_book, 1)
        empty_cart.add(product_pen, 2)

        assert empty_cart.get_item_count() == 3
        assert empty_cart.get_total() == 600.0

    @pytest.mark.negative
    def test_add_zero_quantity_raises_error(self, empty_cart, product_book):
        with pytest.raises(ValueError):
            empty_cart.add(product_book, 0)

    @pytest.mark.negative
    def test_add_negative_quantity_raises_error(self, empty_cart, product_book):
        with pytest.raises(ValueError):
            empty_cart.add(product_book, -1)

    @pytest.mark.negative
    def test_add_more_than_stock_raises_error(self, empty_cart, product_laptop):
        with pytest.raises(ValueError):
            empty_cart.add(product_laptop, 3)

    @pytest.mark.boundary
    def test_add_exactly_stock_amount(self, empty_cart, product_laptop):
        empty_cart.add(product_laptop, 2)

        assert empty_cart.get_item_count() == 2
        assert empty_cart.get_total() == 150000.0

    @pytest.mark.negative
    def test_add_over_stock_by_several_adds_raises_error(self, empty_cart, product_laptop):
        empty_cart.add(product_laptop, 1)

        with pytest.raises(ValueError):
            empty_cart.add(product_laptop, 2)


class TestCartPromo:
    """Промокоды — используйте параметризацию!"""

    @pytest.mark.parametrize(
        "promo_code, expected_total",
        [
            ("SAVE10", 1035.0),
            ("SAVE20", 920.0),
            ("HALF", 575.0),
        ],
    )
    def test_apply_valid_promo_codes(self, cart_with_items, promo_code, expected_total):
        result = cart_with_items.apply_promo(promo_code)

        assert result == expected_total

    @pytest.mark.negative
    def test_apply_unknown_promo_code_raises_error(self, cart_with_items):
        with pytest.raises(ValueError):
            cart_with_items.apply_promo("UNKNOWN")

    @pytest.mark.boundary
    def test_apply_promo_to_empty_cart_returns_zero(self, empty_cart):
        result = empty_cart.apply_promo("SAVE10")

        assert result == 0.0

class TestCartTotal:
    """Расчёт стоимости."""

    def test_empty_cart_total_is_zero(self, empty_cart):
        assert empty_cart.get_total() == 0.0

    @pytest.mark.smoke
    def test_cart_with_items_total(self, cart_with_items):
        assert cart_with_items.get_total() == 1150.0

    def test_total_after_remove_product(self, cart_with_items):
        cart_with_items.remove("Книга")

        assert cart_with_items.get_total() == 150.0

class TestCartRemove:
    """Удаление товаров."""

    def test_remove_existing_product(self, cart_with_items):
        cart_with_items.remove("Книга")

        assert cart_with_items.get_item_count() == 3
        assert cart_with_items.get_total() == 150.0

    def test_remove_only_product_makes_cart_empty(self, empty_cart, product_book):
        empty_cart.add(product_book)
        empty_cart.remove("Книга")

        assert empty_cart.is_empty() is True
        assert empty_cart.get_item_count() == 0
        assert empty_cart.get_total() == 0.0

    @pytest.mark.negative
    def test_remove_unknown_product_raises_error(self, empty_cart):
        with pytest.raises(KeyError):
            empty_cart.remove("Несуществующий товар")

    @pytest.mark.negative
    def test_remove_from_empty_cart_raises_error(self, empty_cart):
        with pytest.raises(KeyError):
            empty_cart.remove("Книга")