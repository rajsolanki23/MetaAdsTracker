import pytest
from backend.services.import_service import ImportService, clean_number


def test_clean_number():
    assert clean_number("$1,250.50") == 1250.50
    assert clean_number(" 3.45% ") == 3.45
    assert clean_number(" - ") == 0.0
    assert clean_number(None) == 0.0
    assert clean_number(42) == 42.0


def test_parse_csv_and_map_columns():
    csv_text = """Ad Name,Amount Spent,Purchase ROAS,Purchases,Impressions,Link Clicks
"Winner Video A","$500.00","3.50","25","10,000","250"
"Loser Static B","$200.00","0.80","2","5,000","40"
"Testing Copy C","$45.00","1.10","1","1,200","15"
"""
    rows = ImportService.parse_raw_text(csv_text)
    assert len(rows) == 3

    mapped_0 = ImportService.map_columns(rows[0])
    assert mapped_0["name"] == "Winner Video A"
    assert mapped_0["spend"] == 500.0
    assert mapped_0["roas"] == 3.50
    assert mapped_0["purchases"] == 25
    assert mapped_0["impressions"] == 10000
    assert mapped_0["clicks"] == 250
    assert mapped_0["ctr"] == 2.5
    assert mapped_0["cpa"] == 20.0


def test_parse_tsv_and_map_columns():
    tsv_text = "Ad\tSpend\tPurchase Conversion Value\tWebsite Purchases\tImpressions\tClicks\n" \
               "Summer Hook 1\t$300.00\t$900.00\t15\t15000\t300\n"
    
    rows = ImportService.parse_raw_text(tsv_text)
    assert len(rows) == 1

    mapped = ImportService.map_columns(rows[0])
    assert mapped["name"] == "Summer Hook 1"
    assert mapped["spend"] == 300.0
    assert mapped["revenue"] == 900.0
    assert mapped["roas"] == 3.0
    assert mapped["purchases"] == 15
