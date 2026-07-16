"""Currency rounding for the sub-cent (NUMERIC(10,3)) revenue totals in reservations.py."""

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def quantize_to_cents(value: Decimal) -> Decimal:
    """Mirrors the rounding step applied in calculate_total_revenue."""
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


class TestSubCentSeedDataRounding:
    def test_sub_cent_reservations_sum_to_a_clean_total(self):
        total = Decimal("333.333") + Decimal("333.333") + Decimal("333.334")
        assert total == Decimal("1000.000")
        assert total.as_tuple().exponent == -3

    def test_unrounded_sub_cent_total_is_not_a_valid_currency_value(self):
        total = Decimal("100.335")
        cents = total * 100
        assert cents != cents.to_integral_value()

    def test_quantize_produces_a_valid_two_decimal_currency_value(self):
        for raw in (Decimal("1000.000"), Decimal("100.335"), Decimal("2249.9951"), Decimal("0.005")):
            rounded = quantize_to_cents(raw)
            assert rounded.as_tuple().exponent == -2
            assert (rounded * 100) == (rounded * 100).to_integral_value()

    def test_quantize_uses_round_half_up_not_bankers_rounding(self):
        """Decimal's default ROUND_HALF_EVEN would give 0.12 here instead of 0.13."""
        assert quantize_to_cents(Decimal("0.125")) == Decimal("0.13")
        assert Decimal("0.125").quantize(CENT) == Decimal("0.12")
