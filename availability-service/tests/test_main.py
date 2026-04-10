from datetime import date

from app.main import date_ranges_overlap


def test_overlap_returns_true_for_crossing_ranges():
    assert date_ranges_overlap(
        date(2026, 5, 1),
        date(2026, 5, 10),
        date(2026, 5, 5),
        date(2026, 5, 15),
    )


def test_overlap_returns_false_for_back_to_back_ranges():
    assert not date_ranges_overlap(
        date(2026, 5, 1),
        date(2026, 5, 10),
        date(2026, 5, 10),
        date(2026, 5, 15),
    )


def test_overlap_returns_false_for_disjoint_ranges():
    assert not date_ranges_overlap(
        date(2026, 5, 1),
        date(2026, 5, 3),
        date(2026, 5, 6),
        date(2026, 5, 8),
    )
