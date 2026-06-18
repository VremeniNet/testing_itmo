"""
СТАРТОВЫЙ ФАЙЛ — Занятие 3. Моки.

Задача:
    Написать тесты для SettlementService, используя MagicMock
    для замены ExchangeRateProvider.

Эталон: tests/unit/test_services.py

Как запустить:
    python -m pytest student_tasks/exercise_4_mocks.py -v
"""

import sys
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from trading_api.calendars import MOEX
from trading_api.services import ExchangeRateProvider, SettlementService


# ══════════════════════════════════════════════════════════════════
#  ФИКСТУРЫ
# ══════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_rate_provider():
    """Пустой мок провайдера курсов (spec для типобезопасности)."""
    return MagicMock(spec=ExchangeRateProvider)


@pytest.fixture
def fixed_rate_provider():
    """Мок, возвращающий курс 100.0 для любой пары/даты."""
    provider = MagicMock(spec=ExchangeRateProvider)
    provider.get_rate.return_value = 100.0
    return provider


@pytest.fixture
def service(fixed_rate_provider):
    """Сервис с MOEX и фиксированным курсом."""
    return SettlementService(fixed_rate_provider, MOEX)


# ══════════════════════════════════════════════════════════════════
#  БАЗА: return_value
# ══════════════════════════════════════════════════════════════════


class TestBasic:

    def test_basic_settlement(self, service, fixed_rate_provider):
        result = service.calculate_settlement(
            trade_date=date(2024, 11, 1),
            base_amount=1000.0,
            base_currency="USD",
            quote_currency="RUB",
        )

        assert result.applied_rate == 100.0
        assert result.quote_amount == 100_000.0
        assert result.settlement_date == date(2024, 11, 6)

    def test_rate_provider_called_correctly(self, service, fixed_rate_provider):
        service.calculate_settlement(
            trade_date=date(2024, 11, 1),
            base_amount=1000.0,
            base_currency="USD",
            quote_currency="RUB",
        )

        fixed_rate_provider.get_rate.assert_called_once_with(
            base="USD",
            quote="RUB",
            on_date=date(2024, 11, 1),
        )


# ══════════════════════════════════════════════════════════════════
#  side_effect как ФУНКЦИЯ — разные значения для разных входов
# ══════════════════════════════════════════════════════════════════


class TestSideEffectFunction:

    def test_different_rates_per_currency(self, mock_rate_provider):
        def rate_lookup(base, quote, on_date):
            rates = {
                ("USD", "RUB"): 97.5,
                ("EUR", "RUB"): 105.2,
            }
            return rates[(base, quote)]

        mock_rate_provider.get_rate.side_effect = rate_lookup
        service = SettlementService(mock_rate_provider, MOEX)

        usd_result = service.calculate_settlement(
            trade_date=date(2024, 11, 1),
            base_amount=1000.0,
            base_currency="USD",
            quote_currency="RUB",
        )
        eur_result = service.calculate_settlement(
            trade_date=date(2024, 11, 1),
            base_amount=1000.0,
            base_currency="EUR",
            quote_currency="RUB",
        )

        assert usd_result.applied_rate == 97.5
        assert eur_result.applied_rate == 105.2
        assert usd_result.quote_amount == 97_500.0
        assert eur_result.quote_amount == 105_200.0
        assert mock_rate_provider.get_rate.call_count == 2

# ══════════════════════════════════════════════════════════════════
#  side_effect как ИСКЛЮЧЕНИЕ — имитация сбоев
# ══════════════════════════════════════════════════════════════════


class TestSideEffectException:

    def test_lookup_error_propagates(self, mock_rate_provider):
        mock_rate_provider.get_rate.side_effect = LookupError("Курс не найден")
        service = SettlementService(mock_rate_provider, MOEX)

        with pytest.raises(LookupError, match="Курс не найден"):
            service.calculate_settlement(
                trade_date=date(2024, 11, 1),
                base_amount=1000.0,
                base_currency="USD",
                quote_currency="RUB",
            )

    def test_connection_error_propagates(self, mock_rate_provider):
        mock_rate_provider.get_rate.side_effect = ConnectionError(
            "Сервис курсов недоступен"
        )
        service = SettlementService(mock_rate_provider, MOEX)

        with pytest.raises(ConnectionError, match="недоступен"):
            service.calculate_settlement(
                trade_date=date(2024, 11, 1),
                base_amount=1000.0,
                base_currency="USD",
                quote_currency="RUB",
            )

# ══════════════════════════════════════════════════════════════════
#  ПРОВЕРКА НЕ-ВЫЗОВОВ: assert_not_called
# ══════════════════════════════════════════════════════════════════


class TestInputValidationDoesntCallMock:
    """
    При невалидных входных данных провайдер НЕ должен вызываться —
    это оптимизация: не тратим HTTP-запрос на заведомо ошибочные данные.
    """

    def test_zero_amount_skips_provider(self, mock_rate_provider):
        def test_zero_amount_skips_provider(self, mock_rate_provider):
            service = SettlementService(mock_rate_provider, MOEX)

            with pytest.raises(ValueError, match="положительным"):
                service.calculate_settlement(
                    trade_date=date(2024, 11, 1),
                    base_amount=0.0,
                    base_currency="USD",
                    quote_currency="RUB",
                )

            mock_rate_provider.get_rate.assert_not_called()