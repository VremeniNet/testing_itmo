from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from bookstore.exceptions import InventoryError, PaymentDeclinedError, PaymentError
from bookstore.interfaces.payment_gateway import PaymentResult, PaymentStatus
from bookstore.models import Address, Book, BookCategory, CartItem, Customer, Order, OrderStatus
from bookstore.order_service import OrderService


def make_book(isbn="9780000000001", price=Decimal("1000"), weight=500):
    return Book(
        isbn=isbn,
        title="Book",
        author="Author",
        category=BookCategory.FICTION,
        base_price=Decimal(price),
        weight_grams=weight,
        publication_year=2024,
    )


def make_order():
    customer = Customer(
        customer_id="C-1",
        name="Daniil",
        email="daniil@example.com",
    )
    return Order(
        order_id="O-1",
        customer=customer,
        items=[CartItem(make_book(), 1)],
    )


def make_address():
    return Address(country="RU", city="Moscow", postal_code="101000", street="Tverskaya")


@pytest.fixture
def dependencies():
    books = MagicMock()
    inventory = MagicMock()
    payment = MagicMock()
    notifications = MagicMock()
    clock = MagicMock()
    clock.now.return_value = datetime(2024, 10, 1)
    return books, inventory, payment, notifications, clock


@pytest.fixture
def service(dependencies):
    return OrderService(*dependencies)


def test_checkout_success_reserves_charges_marks_paid_and_sends_confirmation(service, dependencies):
    _, inventory, payment, notifications, _ = dependencies
    order = make_order()
    inventory.get_stock.return_value = 3
    inventory.reserve.return_value = "R-1"
    payment.charge.return_value = PaymentResult(
        status=PaymentStatus.SUCCESS,
        transaction_id="TX-1",
    )

    result = service.checkout(order, make_address())

    assert order.status == OrderStatus.PAID
    assert order.payment_transaction_id == "TX-1"
    assert result.payment_transaction_id == "TX-1"
    assert result.reservation_ids == ["R-1"]
    inventory.get_stock.assert_called_once_with("9780000000001")
    inventory.reserve.assert_called_once_with("9780000000001", 1)
    payment.charge.assert_called_once_with(
        customer_id="C-1",
        amount=Decimal("1400.00"),
        currency="RUB",
        idempotency_key="order-O-1",
    )
    notifications.send_order_confirmation.assert_called_once_with(order.customer, order)


def test_checkout_does_not_reserve_or_charge_when_stock_is_insufficient(service, dependencies):
    _, inventory, payment, notifications, _ = dependencies
    order = make_order()
    inventory.get_stock.return_value = 0

    with pytest.raises(InventoryError):
        service.checkout(order, make_address())

    assert order.status == OrderStatus.DRAFT
    inventory.reserve.assert_not_called()
    payment.charge.assert_not_called()
    notifications.send_order_confirmation.assert_not_called()


def test_checkout_releases_previous_reservations_when_reserve_fails(service, dependencies):
    _, inventory, payment, _, _ = dependencies
    customer = Customer(customer_id="C-1", name="Daniil", email="daniil@example.com")
    first_book = make_book(isbn="9780000000001")
    second_book = make_book(isbn="9780000000002")
    order = Order(
        order_id="O-1",
        customer=customer,
        items=[CartItem(first_book, 1), CartItem(second_book, 1)],
    )
    inventory.get_stock.return_value = 5
    inventory.reserve.side_effect = ["R-1", InventoryError("reserve failed")]

    with pytest.raises(InventoryError):
        service.checkout(order, make_address())

    inventory.release.assert_called_once_with("R-1")
    payment.charge.assert_not_called()
    assert order.status == OrderStatus.DRAFT


def test_checkout_releases_reservations_and_cancels_order_when_payment_declined(service, dependencies):
    _, inventory, payment, _, _ = dependencies
    order = make_order()
    inventory.get_stock.return_value = 3
    inventory.reserve.return_value = "R-1"
    payment.charge.return_value = PaymentResult(
        status=PaymentStatus.DECLINED,
        decline_reason="Недостаточно средств",
    )

    with pytest.raises(PaymentDeclinedError):
        service.checkout(order, make_address())

    assert order.status == OrderStatus.CANCELLED
    inventory.release.assert_called_with("R-1")


def test_checkout_releases_reservations_and_cancels_order_when_gateway_raises_error(service, dependencies):
    _, inventory, payment, _, _ = dependencies
    order = make_order()
    inventory.get_stock.return_value = 3
    inventory.reserve.return_value = "R-1"
    payment.charge.side_effect = PaymentError("gateway unavailable")

    with pytest.raises(PaymentError):
        service.checkout(order, make_address())

    assert order.status == OrderStatus.CANCELLED
    inventory.release.assert_called_once_with("R-1")


def test_checkout_stays_paid_when_notification_fails(service, dependencies):
    _, inventory, payment, notifications, _ = dependencies
    order = make_order()
    inventory.get_stock.return_value = 3
    inventory.reserve.return_value = "R-1"
    payment.charge.return_value = PaymentResult(
        status=PaymentStatus.SUCCESS,
        transaction_id="TX-1",
    )
    notifications.send_order_confirmation.side_effect = RuntimeError("email failed")

    result = service.checkout(order, make_address())

    assert order.status == OrderStatus.PAID
    assert result.payment_transaction_id == "TX-1"