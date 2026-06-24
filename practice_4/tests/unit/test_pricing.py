from datetime import datetime
from decimal import Decimal

import pytest

from bookstore.exceptions import PricingError
from bookstore.models import Book, BookCategory, CartItem, Customer, CustomerTier, Order
from bookstore.pricing import PricingService


def make_book(
    isbn="9780000000001",
    price=Decimal("1000"),
    weight=500,
    category=BookCategory.FICTION,
):
    return Book(
        isbn=isbn,
        title="Book",
        author="Author",
        category=category,
        base_price=Decimal(price),
        weight_grams=weight,
        publication_year=2024,
    )


def make_order(
    items,
    tier=CustomerTier.BRONZE,
    promo_code=None,
    is_blocked=False,
):
    customer = Customer(
        customer_id="C-1",
        name="Daniil",
        email="daniil@example.com",
        tier=tier,
        is_blocked=is_blocked,
    )
    return Order(
        order_id="O-1",
        customer=customer,
        items=items,
        promo_code=promo_code,
    )


def test_silver_order_matches_requirements_example():
    service = PricingService()
    book = make_book(price=Decimal("1500"), weight=600)
    order = make_order([CartItem(book, 2)], tier=CustomerTier.SILVER)

    result = service.calculate_order_total(order, datetime(2024, 10, 1))

    assert result.subtotal == Decimal("3000")
    assert result.discount_amount == Decimal("150.00")
    assert result.subtotal_after_discount == Decimal("2850.00")
    assert result.delivery_fee == Decimal("302")
    assert result.vat == Decimal("285.00")
    assert result.total == Decimal("3437.00")


def test_gold_order_gets_tier_discount_and_free_delivery():
    service = PricingService()
    book = make_book(price=Decimal("5000"), weight=800)
    order = make_order([CartItem(book, 1)], tier=CustomerTier.GOLD)

    result = service.calculate_order_total(order, datetime(2024, 10, 1))

    assert result.discount_rate == Decimal("0.10")
    assert result.discount_amount == Decimal("500.00")
    assert result.subtotal_after_discount == Decimal("4500.00")
    assert result.delivery_fee == Decimal("0")
    assert result.vat == Decimal("450.00")
    assert result.total == Decimal("4950.00")


def test_welcome_promo_is_used_when_better_than_customer_tier():
    service = PricingService()
    book = make_book(price=Decimal("2000"), weight=900)
    order = make_order(
        [CartItem(book, 1)],
        tier=CustomerTier.BRONZE,
        promo_code="WELCOME15",
    )

    result = service.calculate_order_total(order, datetime(2024, 10, 1))

    assert result.discount_rate == Decimal("0.15")
    assert result.discount_amount == Decimal("300.00")
    assert result.subtotal_after_discount == Decimal("1700.00")


def test_student_promo_applies_to_textbooks_only_order():
    service = PricingService()
    textbook = make_book(category=BookCategory.TEXTBOOK, price=Decimal("1000"))
    order = make_order([CartItem(textbook, 2)], promo_code="STUDENT25")

    result = service.calculate_order_total(order, datetime(2024, 10, 1))

    assert result.discount_rate == Decimal("0.25")
    assert result.discount_amount == Decimal("500.00")


def test_student_promo_does_not_apply_to_mixed_order():
    service = PricingService()
    textbook = make_book(
        isbn="9780000000001",
        category=BookCategory.TEXTBOOK,
        price=Decimal("1000"),
    )
    fiction = make_book(
        isbn="9780000000002",
        category=BookCategory.FICTION,
        price=Decimal("1000"),
    )
    order = make_order(
        [CartItem(textbook, 1), CartItem(fiction, 1)],
        promo_code="STUDENT25",
    )

    result = service.calculate_order_total(order, datetime(2024, 10, 1))

    assert result.discount_rate == Decimal("0")
    assert result.discount_amount == Decimal("0.00")


def test_black_friday_discount_is_best_discount():
    service = PricingService()
    book = make_book(price=Decimal("1000"))
    order = make_order(
        [CartItem(book, 1)],
        tier=CustomerTier.GOLD,
        promo_code="WELCOME15",
    )

    result = service.calculate_order_total(order, datetime(2024, 11, 24))

    assert result.discount_rate == Decimal("0.30")
    assert result.discount_amount == Decimal("300.00")


def test_rare_books_are_not_discounted():
    service = PricingService()
    fiction = make_book(
        isbn="9780000000001",
        category=BookCategory.FICTION,
        price=Decimal("1000"),
    )
    rare = make_book(
        isbn="9780000000002",
        category=BookCategory.RARE,
        price=Decimal("1000"),
    )
    order = make_order(
        [CartItem(fiction, 1), CartItem(rare, 1)],
        tier=CustomerTier.GOLD,
    )

    result = service.calculate_order_total(order, datetime(2024, 10, 1))

    assert result.discountable_subtotal == Decimal("1000")
    assert result.non_discountable_subtotal == Decimal("1000")
    assert result.discount_amount == Decimal("100.00")
    assert result.subtotal_after_discount == Decimal("1900.00")


def test_children_book_makes_delivery_free():
    service = PricingService()
    book = make_book(category=BookCategory.CHILDREN, price=Decimal("500"), weight=1500)
    order = make_order([CartItem(book, 1)])

    result = service.calculate_order_total(order, datetime(2024, 10, 1))

    assert result.delivery_fee == Decimal("0")


@pytest.mark.parametrize(
    "order",
    [
        make_order([]),
        make_order([CartItem(make_book(), 0)]),
        make_order([CartItem(make_book(), 21)]),
        make_order([CartItem(make_book(price=Decimal("100001")), 1)]),
        make_order([CartItem(make_book(), 1)], is_blocked=True),
    ],
)
def test_invalid_orders_raise_pricing_error(order):
    service = PricingService()

    with pytest.raises(PricingError):
        service.calculate_order_total(order, datetime(2024, 10, 1))


def test_unknown_promo_raises_pricing_error():
    service = PricingService()
    order = make_order([CartItem(make_book(), 1)], promo_code="UNKNOWN")

    with pytest.raises(PricingError):
        service.calculate_order_total(order, datetime(2024, 10, 1))