import test_scoring, test_roadmap, test_bullets, test_classification

test_scoring.test_score_breakdown()
test_scoring.test_score_breakdown_inconsistent()
test_scoring.test_score_breakdown_overlap()

test_roadmap.test_order_steps()

test_bullets.test_is_unsafe_bullet()

test_classification.test_categorize()

print("ALL TESTS PASSED")
