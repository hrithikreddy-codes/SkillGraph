from analyzer import order_steps

def test_order_steps():
    steps = [
        {"skill": "CI/CD", "priority": "High"},
        {"skill": "Jest", "priority": "Medium"},
        {"skill": "React", "priority": "Medium"},
        {"skill": "Unit Testing", "priority": "High"},
        {"skill": "Integration Testing", "priority": "Low"}
    ]
    
    ordered = order_steps(steps)
    assert len(ordered) == 5
    skills = [s["skill"] for s in ordered]
    
    # Check dependencies
    assert skills.index("Unit Testing") < skills.index("Integration Testing")
    assert skills.index("Jest") < skills.index("CI/CD")
