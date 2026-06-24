from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from bookstore.api import (
    app,
    get_customers_storage,
    get_order_service,
    get_orders_storage,
)
from bookstore.exceptions import (
    InventoryError,
    OrderError,
    PaymentDeclinedError,
    PaymentError,
    PricingError,
)
from bookstore.models import Book, BookCategory, CartItem, Customer, Order, OrderStatus
from bookstore.order_service import CheckoutResult


def make_customer(customer_id="C-1", is_blocked=False):
    return Customer(
        customer_id=customer_id,
        name="Daniil",
        email="daniil@example.com",
        is_blocked=is_blocked,
    )


def make_book(isbn="9780000000001"):
    return Book(
        isbn=isbn,
        title="Book",
        author="Author",
        category=BookCategory.FICTION,
        base_price=Decimal("1000"),
        weight_grams=500,
        publication_year=2024,
    )


def make_order(order_id="O-1", customer=None):
    if customer is None:
        customer = make_customer()
    return Order(
        order_id=order_id,
        customer=customer,
        items=[CartItem(make_book(), 1)],
    )


@pytest.fixture
def service():
    return MagicMock()


@pytest.fixture
def customers():
    return {"C-1": make_customer()}


@pytest.fixture
def orders():
    return {"O-1": make_order()}


@pytest.fixture
def client(service, customers, orders):
    app.dependency_overrides[get_order_service] = lambda: service
    app.dependency_overrides[get_customers_storage] = lambda: customers
    app.dependency_overrides[get_orders_storage] = lambda: orders

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_create_order_returns_201_and_order_schema(client, service, customers):
    order = Order(order_id="O-2", customer=customers["C-1"])
    service.create_order.return_value = order

    response = client.post("/orders", json={"customer_id": "C-1"})
    body = response.json()

    assert response.status_code == 201
    assert set(body) == {
        "order_id",
        "status",
        "customer_id",
        "items_count",
        "subtotal",
        "promo_code",
    }
    assert body["order_id"] == "O-2"
    assert body["status"] == "DRAFT"
    assert body["customer_id"] == "C-1"


def test_create_order_for_blocked_customer_returns_403(client, service):
    service.create_order.side_effect = OrderError("Покупатель заблокирован")

    response = client.post("/orders", json={"customer_id": "C-1"})

    assert response.status_code == 403


def test_get_unknown_order_returns_404(client):
    response = client.get("/orders/UNKNOWN")

    assert response.status_code == 404


def test_invalid_add_item_body_returns_422(client):
    response = client.post(
        "/orders/O-1/items",
        json={"isbn": "9780000000001", "quantity": 0},
    )

    assert response.status_code == 422


def test_checkout_pricing_error_returns_422(client, service):
    service.checkout.side_effect = PricingError("Заказ не может быть пустым")

    response = client.post(
        "/orders/O-1/checkout",
        json={
            "shipping_address": {
                "country": "RU",
                "city": "Moscow",
                "postal_code": "101000",
                "street": "Tverskaya",
            }
        },
    )

    assert response.status_code == 422


def test_checkout_inventory_error_returns_409(client, service):
    service.checkout.side_effect = InventoryError("Недостаточно товара")

    response = client.post(
        "/orders/O-1/checkout",
        json={
            "shipping_address": {
                "country": "RU",
                "city": "Moscow",
                "postal_code": "101000",
                "street": "Tverskaya",
            }
        },
    )

    assert response.status_code == 409


def test_checkout_payment_declined_returns_402(client, service):
    service.checkout.side_effect = PaymentDeclinedError("Платёж отклонён")

    response = client.post(
        "/orders/O-1/checkout",
        json={
            "shipping_address": {
                "country": "RU",
                "city": "Moscow",
                "postal_code": "101000",
                "street": "Tverskaya",
            }
        },
    )

    assert response.status_code == 402


def test_checkout_gateway_error_returns_502(client, service):
    service.checkout.side_effect = PaymentError("Ошибка платёжного шлюза")

    response = client.post(
        "/orders/O-1/checkout",
        json={
            "shipping_address": {
                "country": "RU",
                "city": "Moscow",
                "postal_code": "101000",
                "street": "Tverskaya",
            }
        },
    )

    assert response.status_code == 502


def test_successful_checkout_response_matches_schema(client, service, orders):
    order = orders["O-1"]
    order.status = OrderStatus.PAID

    service.checkout.return_value = CheckoutResult(
        order=order,
        total=Decimal("1400.00"),
        payment_transaction_id="TX-1",
        reservation_ids=["R-1"],
    )

    response = client.post(
        "/orders/O-1/checkout",
        json={
            "shipping_address": {
                "country": "RU",
                "city": "Moscow",
                "postal_code": "101000",
                "street": "Tverskaya",
            }
        },
    )
    body = response.json()

    assert response.status_code == 200
    assert set(body) == {"order_id", "status", "total", "transaction_id"}
    assert body["order_id"] == "O-1"
    assert body["status"] == "PAID"
    assert body["transaction_id"] == "TX-1"