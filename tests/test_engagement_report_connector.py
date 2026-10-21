"""Unit tests for the Iceberg-safe column name sanitizer (Bronze layer)."""

from engagement_report_connector import sanitize_column_names


def test_spaces_are_replaced_with_underscores():
    assert sanitize_column_names(["Hours Viewed"]) == ["Hours_Viewed"]


def test_parentheses_are_removed():
    assert sanitize_column_names(["Runtime (hours)"]) == ["Runtime_hours"]


def test_already_clean_names_are_unchanged():
    columns = ["Title", "content_type"]

    assert sanitize_column_names(columns) == ["Title", "content_type"]


def test_empty_list_returns_empty_list():
    assert sanitize_column_names([]) == []


def test_input_list_is_not_modified():
    original = ["Hours Viewed"]

    sanitize_column_names(original)

    assert original == ["Hours Viewed"]