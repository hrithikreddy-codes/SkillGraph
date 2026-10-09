import unittest.mock
import analyzer
from analyzer import compare

def test_compare_offline():
    resume_text = "I know Python, React, MySQL, and Git."
    
    resume_data = {
        "skills": ["Python", "React", "MySQL", "Git"]
    }
    
    job_data = {
        "required_skills": ["Python", "React", "Docker", "TypeScript"],
        "alternatives": [["PostgreSQL", "MySQL"]],
        "nice_to_have_skills": ["Redis"],
        "soft_skills": ["Teamwork"]
    }
    
    fake_verify = {
        "results": [
            {
                "skill": "Docker", 
                "status": "missing", 
                "evidence": "", 
                "reason": "Not demonstrated in the resume", 
                "confidence": "high", 
                "what_is_missing": "", 
                "evidence_type": "explicit"
            },
            {
                "skill": "TypeScript", 
                "status": "partial", 
                "evidence": "JavaScript, React", 
                "reason": "Related experience found", 
                "confidence": "medium", 
                "what_is_missing": "Found: JavaScript, React. Not found: direct TypeScript typing", 
                "evidence_type": "project"
            }
        ]
    }
    
    fake_find = {
        "results": [
            {
                "skill": "Python", 
                "evidence": "Built a prediction model", 
                "where": "Project"
            }
        ]
    }
    
    with unittest.mock.patch("analyzer.verify_missing_skills", return_value=fake_verify), \
         unittest.mock.patch("analyzer.find_evidence", return_value=fake_find):
        result = compare(resume_text, resume_data, job_data)
    
    matched = result.get("matched", [])
    partial = result.get("partial", [])
    missing = result.get("missing", [])
    
    # Python and React are matched
    assert "Python" in matched, "Python should be matched"
    assert "React" in matched, "React should be matched"
    
    # Docker stays in missing, TypeScript ends up in partial
    assert "Docker" in missing, "Docker should be missing"
    assert "TypeScript" in partial, "TypeScript should be partial"
    assert "TypeScript" not in missing, "TypeScript should not be missing"
    
    # The PostgreSQL/MySQL group counts as ONE matched requirement (MySQL is matched)
    assert "MySQL" in matched, "MySQL from alternatives should be matched"
    
    # Redis does not affect the required count
    assert "Redis" not in matched, "Redis is nice-to-have, should not be in matched"
    assert "Redis" not in missing, "Redis is nice-to-have, should not be in missing"
    assert "Redis" not in partial, "Redis is nice-to-have, should not be in partial"
    
    # Teamwork is not in matched or missing
    assert "Teamwork" not in matched, "Teamwork is soft skill, should not be in matched"
    assert "Teamwork" not in missing, "Teamwork is soft skill, should not be in missing"
    assert "Teamwork" not in partial, "Teamwork is soft skill, should not be in partial"
    
    # compare_result gaps and evidence checks
    assert "Not found" in result.get("gaps", {}).get("TypeScript", ""), "Gaps for TypeScript should contain 'Not found'"
    assert result.get("evidence", {}).get("Python") == "Built a prediction model", "Evidence for Python must be set"
    
    # Every skill appears in exactly one of matched/partial/missing
    all_core = set(["Python", "React", "Docker", "TypeScript", "MySQL"])
    all_returned = set(matched + partial + missing)
    assert all_core == all_returned, "The returned skills should exactly match the core requirements"
    
    intersection1 = set(matched).intersection(set(partial))
    intersection2 = set(matched).intersection(set(missing))
    intersection3 = set(partial).intersection(set(missing))
    assert not intersection1 and not intersection2 and not intersection3, "Skills should not overlap between matched/partial/missing"
    
    # The returned dict contains the keys evidence, reasons, gaps, confidence and evidence_type
    for key in ["evidence", "reasons", "gaps", "confidence", "evidence_type"]:
        assert key in result, f"Result must contain key: {key}"
        
    print("All compare tests passed")

if __name__ == "__main__":
    test_compare_offline()
