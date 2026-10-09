from analyzer import categorize

def test_categorize():
    assert categorize("React") == "Frontend"
    assert categorize("Node.js") == "Backend"
    assert categorize("UnknownSkill") == "Other"
    
    assert categorize("Unit Testing with Jest") == "Testing"
    assert categorize("AWS / Azure") == "DevOps & Cloud"
