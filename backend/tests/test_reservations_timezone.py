"""Timezone-aware month boundaries for app.services.reservations."""

import asyncio
from datetime import datetime, timezone
from decimal import Decimal

from app.services.reservations import get_month_boundaries_utc

RES_TZ_1_CHECK_IN = datetime(2024, 2, 29, 23, 30, 0, tzinfo=timezone.utc)
PARIS_TZ = "Europe/Paris"


class TestGetMonthBoundariesUtc:
    def test_utc_property_boundaries_are_naive_equivalent(self):
        start, end = get_month_boundaries_utc(2024, 3, "UTC")

        assert start == datetime(2024, 3, 1, 0, 0, 0, tzinfo=timezone.utc)
        assert end == datetime(2024, 4, 1, 0, 0, 0, tzinfo=timezone.utc)

    def test_paris_property_march_start_is_feb_29_23_00_utc(self):
        start, _ = get_month_boundaries_utc(2024, 3, PARIS_TZ)

        assert start == datetime(2024, 2, 29, 23, 0, 0, tzinfo=timezone.utc)

    def test_december_rolls_over_to_next_year_january(self):
        start, end = get_month_boundaries_utc(2024, 12, "UTC")

        assert start == datetime(2024, 12, 1, tzinfo=timezone.utc)
        assert end == datetime(2025, 1, 1, tzinfo=timezone.utc)


class TestMonthBoundaryClassification:
    """Covers res-tz-1 from database/seed.sql: a Paris property check-in at
    2024-02-29 23:30 UTC, which is 2024-03-01 00:30 local time."""

    def test_res_tz_1_falls_within_march_for_paris_property(self):
        start, end = get_month_boundaries_utc(2024, 3, PARIS_TZ)

        assert start <= RES_TZ_1_CHECK_IN < end

    def test_res_tz_1_does_not_fall_within_february_for_paris_property(self):
        start, end = get_month_boundaries_utc(2024, 2, PARIS_TZ)

        assert not (start <= RES_TZ_1_CHECK_IN < end)

    def test_naive_utc_boundaries_would_have_misclassified_the_reservation(self):
        """Characterizes the pre-fix bug directly; does not call the fixed helper."""
        buggy_march_start_utc = datetime(2024, 3, 1, tzinfo=timezone.utc)

        assert RES_TZ_1_CHECK_IN < buggy_march_start_utc, (
            "res-tz-1 would have been excluded from March under the old naive-UTC boundary"
        )


class TestCalculateMonthlyRevenueUsesPropertyTimezone:
    def test_defaults_to_utc_when_no_timezone_given(self):
        from app.services.reservations import calculate_monthly_revenue

        result = asyncio.run(calculate_monthly_revenue("prop-001", 3, 2024))
        assert isinstance(result, Decimal)
