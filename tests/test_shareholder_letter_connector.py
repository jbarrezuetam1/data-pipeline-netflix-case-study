"""Unit tests for the PDF regional-breakdown parser (Bronze layer)."""

from shareholder_letter_connector import parse_regional_breakdown

QUARTERS = ["Q2'25", "Q3'25", "Q4'25", "Q1'26", "Q2'26"]


def test_single_region_single_metric_produces_one_record_per_quarter():
    blob = "UCAN:\nRevenue 4929 5072 5339 5245 5432"

    records = parse_regional_breakdown(blob, QUARTERS)

    assert len(records) == 5
    assert records[0] == {
        "region": "UCAN",
        "metric": "Revenue",
        "quarter": "Q2'25",
        "value": "4929",
    }
    assert records[-1]["quarter"] == "Q2'26"
    assert records[-1]["value"] == "5432"


def test_region_header_colon_is_removed():
    blob = "EMEA:\nRevenue 1 2 3 4 5"

    records = parse_regional_breakdown(blob, QUARTERS)

    assert all(r["region"] == "EMEA" for r in records)


def test_metrics_are_assigned_to_the_most_recent_region():
    blob = (
        "UCAN:\n"
        "Revenue 1 2 3 4 5\n"
        "EMEA:\n"
        "Revenue 6 7 8 9 10"
    )

    records = parse_regional_breakdown(blob, QUARTERS)

    ucan_values = [r["value"] for r in records if r["region"] == "UCAN"]
    emea_values = [r["value"] for r in records if r["region"] == "EMEA"]
    assert ucan_values == ["1", "2", "3", "4", "5"]
    assert emea_values == ["6", "7", "8", "9", "10"]


def test_multi_word_metric_name_is_preserved():
    blob = "APAC:\nY/Y Growth Rate 24% 21% 17% 20% 16%"

    records = parse_regional_breakdown(blob, QUARTERS)

    assert records[0]["metric"] == "Y/Y Growth Rate"
    assert records[0]["value"] == "24%"


def test_blank_lines_are_ignored():
    blob = "\nLATAM:\n\nRevenue 1 2 3 4 5\n\n"

    records = parse_regional_breakdown(blob, QUARTERS)

    assert len(records) == 5


def test_total_record_count_is_regions_times_metrics_times_quarters():
    blob = (
        "UCAN:\nRevenue 1 2 3 4 5\nGrowth 1 2 3 4 5\n"
        "EMEA:\nRevenue 1 2 3 4 5\nGrowth 1 2 3 4 5"
    )

    records = parse_regional_breakdown(blob, QUARTERS)

    assert len(records) == 2 * 2 * 5