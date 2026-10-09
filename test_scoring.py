from analyzer import score_breakdown

def test_score_breakdown():
    result = score_breakdown({
        "matched": ["A"],
        "partial": ["B"],
        "missing": ["C", "D"],
        "match_percent": 38
    })
    
    assert result["total_required"] == 4
    assert result["matched_count"] == 1
    assert result["partial_count"] == 1
    assert result["missing_count"] == 2
    assert result["match_percent"] == 38
    assert result["consistent"] is True

def test_score_breakdown_inconsistent():
    result = score_breakdown({
        "matched": ["A"],
        "partial": ["B"],
        "missing": ["C", "D"],
        "match_percent": 99  # incorrect
    })
    assert result["consistent"] is False

def test_score_breakdown_overlap():
    result = score_breakdown({
        "matched": ["A", "B"],
        "partial": ["B"],
        "missing": ["C"],
        "match_percent": 62
    })
    assert result["consistent"] is False
