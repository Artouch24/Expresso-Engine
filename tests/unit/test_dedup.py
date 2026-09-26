from poker_tracker.winamax.dedup import unique_by


def test_deduplicates_by_domain_id_not_filename():
    items = [
        {"hand_id": "H1", "file": "a"},
        {"hand_id": "H1", "file": "b"},
        {"hand_id": "H2", "file": "b"},
    ]
    assert [x["hand_id"] for x in unique_by(items, lambda x: x["hand_id"])] == ["H1", "H2"]


def test_same_tournament_can_merge_hands_from_files():
    hands = [("T1", "H1"), ("T1", "H2")]
    assert len(unique_by(hands, lambda x: x[0])) == 1
    assert len(unique_by(hands, lambda x: x[1])) == 2
