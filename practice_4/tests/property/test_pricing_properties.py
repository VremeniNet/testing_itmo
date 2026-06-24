from datetime import datetime
from decimal import Decimal

from hypothesis import given, strategies as st

from bookstore.models import Book, BookCategory, CartItem, Customer, CustomerTier, Order
from bookstore.pricing import PricingService


categories = st.sampled_from(list(BookCategory))
tiers = st.sampled_from(list(CustomerTier))
prices = st.integers(min_value=1, max_value=5000)
weights = st.integers(min_value=1, max_value=5000)
quantities = st.integers(min_value=1, max_value=20)


def make_book(category, price, weight):
    return Book(
        isbn="9780000000001",
        title="Book",
        author="Author",
        category=category,
        base_price=Decimal(price),
        weight_grams=weight,
        publication_year=2024,
    )


def make_order(book, quantity, tier=CustomerTier.BRONZE, promo_code=None):
    customer = Customer(
        customer_id="C-1",
        name="Daniil",
        email="daniil@example.com",
        tier=tier,
    )
    return Order(
        order_id="O-1",
        customer=customer,
        items=[CartItem(book, quantity)],
        promo_code=promo_code,
    )


@given(category=categories, tier=tiers, price=prices, weight=weights, quantity=quantities)
def test_total_equals_sum_of_components(category, tier, price, weight, quantity):
    book = make_book(category, price, weight)
    order = make_order(book, quantity, tier=tier)

    result = PricingService().calculate_order_total(order, datetime(2024, 10, 1))

    assert result.total == result.subtotal_after_discount + result.delivery_fee + result.vat


@given(category=categories, price=prices, weight=weights, quantity=quantities)
def test_vat_is_ten_percent_of_subtotal_after_discount(category, price, weight, quantity):
    book = make_book(category, price, weight)
    order = make_order(book, quantity)

    result = PricingService().calculate_order_total(order, datetime(2024, 10, 1))

    assert result.vat == (
        result.subtotal_after_discount * Decimal("0.10")
    ).quantize(Decimal("0.01"))


@given(price=prices, weight=weights, quantity=quantities)
def test_children_book_always_has_free_delivery(price, weight, quantity):
    book = make_book(BookCategory.CHILDREN, price, weight)
    order = make_order(book, quantity)

    result = PricingService().calculate_order_total(order, datetime(2024, 10, 1))

    assert result.delivery_fee == Decimal("0")


@given(tier=tiers, price=prices, weight=weights, quantity=quantities)
def test_rare_books_are_not_discounted(tier, price, weight, quantity):
    book = make_book(BookCategory.RARE, price, weight)
    order = make_order(book, quantity, tier=tier, promo_code="WELCOME15")

    result = PricingService().calculate_order_total(order, datetime(2024, 11, 24))

    assert result.discountable_subtotal == Decimal("0")
    assert result.discount_amount == Decimal("0.00")
    assert result.subtotal_after_discount == result.subtotal


@given(price=st.integers(min_value=1, max_value=1000), weight=weights)
def test_delivery_for_light_order_has_base_fee(price, weight):
    book = make_book(BookCategory.FICTION, price, weight)
    order = make_order(book, 1)

    result = PricingService().calculate_order_total(order, datetime(2024, 10, 1))

    assert result.delivery_fee >= Decimal("300")