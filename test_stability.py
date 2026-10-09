import os
import sys

# Ensure the analyzer can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyzer import extract_job_skills

JOB_DESCRIPTION = """
Frontend Developer
==================

We are looking for an experienced developer to join our team.

Responsibilities:
- Build modern user interfaces using React and TypeScript.
- Develop scalable backend services using Node.js.
- Write robust unit and integration tests with Jest.
- Set up and maintain CI/CD pipelines with GitHub Actions.
- Containerize applications using Docker.
- Deploy and manage infrastructure on AWS.
- Participate in Agile/Scrum ceremonies including daily standups and sprint planning.

Requirements:
- Strong problem-solving abilities and good communication skills to work effectively in a team environment.
"""

def main():
    print("Testing stability of extract_job_skills...")
    runs = []
    
    for i in range(5):
        print(f"\n--- Run {i+1} ---")
        result = extract_job_skills(JOB_DESCRIPTION)
        
        req_skills = result.get("required_skills", [])
        soft_skills = result.get("soft_skills", [])
        
        # Ensure it's sorted for comparison
        req_skills_sorted = sorted(req_skills)
        
        print(f"Number of required_skills: {len(req_skills_sorted)}")
        print(f"required_skills (sorted): {req_skills_sorted}")
        print(f"soft_skills: {soft_skills}")
        
        runs.append(req_skills_sorted)
        
    # Check stability
    print("\n--- Stability Check ---")
    is_stable = True
    base_run = runs[0]
    
    for i, run in enumerate(runs[1:], 1):
        if run != base_run:
            is_stable = False
            diff_added = set(run) - set(base_run)
            diff_removed = set(base_run) - set(run)
            print(f"Run {i+1} differed from Run 1.")
            if diff_added:
                print(f"  Added: {diff_added}")
            if diff_removed:
                print(f"  Removed: {diff_removed}")
                
    if is_stable:
        print("STABLE")
    else:
        print("UNSTABLE")

if __name__ == "__main__":
    main()
