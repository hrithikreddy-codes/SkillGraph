from analyzer import is_unsafe_bullet

def test_is_unsafe_bullet():
    # Numbers
    assert is_unsafe_bullet("Led a team of 5") is True
    # Percentages
    assert is_unsafe_bullet("Improved efficiency by 20%") is True
    # Banned words
    assert is_unsafe_bullet("Ensuring high quality") is True
    assert is_unsafe_bullet("Optimal performance") is True
    
    # Safe
    assert is_unsafe_bullet("Built a React frontend for the application") is False
    assert is_unsafe_bullet("Integrated Stripe API") is False
