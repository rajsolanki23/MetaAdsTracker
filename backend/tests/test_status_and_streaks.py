import pytest
from backend.services.leaderboard_service import (
    evaluate_status,
    calculate_streak,
    calculate_rank_movement,
    build_leaderboard_items,
    aggregate_client_summary
)


def test_evaluate_status_rules():
    target_roas = 2.5
    min_spend = 100.0

    # 1. Below minimum spend -> TESTING
    assert evaluate_status(spend=50.0, roas=3.0, target_roas=target_roas, min_spend_threshold=min_spend) == "TESTING"
    assert evaluate_status(spend=0.0, roas=0.0, target_roas=target_roas, min_spend_threshold=min_spend) == "TESTING"

    # 2. Spend >= min_spend and roas >= target -> WIN
    assert evaluate_status(spend=150.0, roas=2.5, target_roas=target_roas, min_spend_threshold=min_spend) == "WIN"
    assert evaluate_status(spend=500.0, roas=4.2, target_roas=target_roas, min_spend_threshold=min_spend) == "WIN"

    # 3. Spend >= min_spend and roas < target -> LOSS
    assert evaluate_status(spend=100.0, roas=2.49, target_roas=target_roas, min_spend_threshold=min_spend) == "LOSS"
    assert evaluate_status(spend=1200.0, roas=0.8, target_roas=target_roas, min_spend_threshold=min_spend) == "LOSS"

    # 4. Status override -> PAUSED
    assert evaluate_status(spend=500.0, roas=5.0, target_roas=target_roas, min_spend_threshold=min_spend, status_override="PAUSED") == "PAUSED"


def test_calculate_streak():
    # Empty history
    assert calculate_streak([]) == 0

    # Consecutive WINs (flame streak)
    assert calculate_streak(["WIN"]) == 1
    assert calculate_streak(["LOSS", "WIN", "WIN", "WIN"]) == 3
    assert calculate_streak(["TESTING", "WIN", "WIN", "WIN", "WIN", "WIN"]) == 5

    # Consecutive LOSSes (ice streak)
    assert calculate_streak(["LOSS"]) == -1
    assert calculate_streak(["WIN", "LOSS", "LOSS"]) == -2
    assert calculate_streak(["TESTING", "LOSS", "LOSS", "LOSS", "LOSS"]) == -4

    # Latest is TESTING or PAUSED -> 0
    assert calculate_streak(["WIN", "WIN", "TESTING"]) == 0
    assert calculate_streak(["WIN", "WIN", "PAUSED"]) == 0


def test_calculate_rank_movement():
    # New creative (no yesterday rank)
    assert calculate_rank_movement(today_rank=1, yesterday_rank=None) == ("NEW", 0)

    # Climbed rank (today #1, yesterday #3 -> climbed 2 spots)
    assert calculate_rank_movement(today_rank=1, yesterday_rank=3) == ("UP_2", 2)
    assert calculate_rank_movement(today_rank=4, yesterday_rank=10) == ("UP_6", 6)

    # Dropped rank (today #5, yesterday #2 -> dropped 3 spots)
    assert calculate_rank_movement(today_rank=5, yesterday_rank=2) == ("DOWN_3", -3)
    assert calculate_rank_movement(today_rank=2, yesterday_rank=1) == ("DOWN_1", -1)

    # Unchanged rank
    assert calculate_rank_movement(today_rank=3, yesterday_rank=3) == ("SAME", 0)


def test_build_leaderboard_items_ranking_and_streaks():
    client_id = "client_1"
    clients_map = {
        client_id: {
            "_id": client_id,
            "name": "Acme Brand",
            "target_roas": 2.5,
            "min_spend_threshold": 100.0
        }
    }

    creatives = [
        {"_id": "c1", "client_id": client_id, "name": "Ad High ROAS", "first_seen_date": "2026-08-20"},
        {"_id": "c2", "client_id": client_id, "name": "Ad Low ROAS", "first_seen_date": "2026-08-20"},
        {"_id": "c3", "client_id": client_id, "name": "Ad Testing", "first_seen_date": "2026-08-24"},
    ]

    snapshots_by_creative = {
        "c1": [
            {"date": "2026-08-23", "spend": 200.0, "revenue": 600.0, "roas": 3.0, "rank": 2},
            {"date": "2026-08-24", "spend": 250.0, "revenue": 1000.0, "roas": 4.0, "impressions": 10000, "clicks": 200, "purchases": 20}
        ],
        "c2": [
            {"date": "2026-08-23", "spend": 300.0, "revenue": 300.0, "roas": 1.0, "rank": 1},
            {"date": "2026-08-24", "spend": 400.0, "revenue": 400.0, "roas": 1.0, "impressions": 20000, "clicks": 300, "purchases": 8}
        ],
        "c3": [
            {"date": "2026-08-24", "spend": 40.0, "revenue": 50.0, "roas": 1.25, "impressions": 2000, "clicks": 30, "purchases": 1}
        ]
    }

    items = build_leaderboard_items(
        creatives=creatives,
        clients_map=clients_map,
        snapshots_by_creative=snapshots_by_creative,
        target_date="2026-08-24",
        yesterday_date="2026-08-23",
        sort_by="roas",
        sort_dir="desc"
    )

    assert len(items) == 3
    # c1 has ROAS 4.0 -> Rank 1 (climbed from 2 -> UP_1)
    assert items[0].id == "c1"
    assert items[0].rank == 1
    assert items[0].status == "WIN"
    assert items[0].streak == 2  # 2 consecutive WINs
    assert items[0].rank_movement == "UP_1"

    # c3 has ROAS 1.25 -> Rank 2 (NEW)
    assert items[1].id == "c3"
    assert items[1].rank == 2
    assert items[1].status == "TESTING"
    assert items[1].rank_movement == "NEW"

    # c2 has ROAS 1.0 -> Rank 3 (dropped from 1 -> DOWN_2)
    assert items[2].id == "c2"
    assert items[2].rank == 3
    assert items[2].status == "LOSS"
    assert items[2].streak == -2  # 2 consecutive LOSSes
    assert items[2].rank_movement == "DOWN_2"
