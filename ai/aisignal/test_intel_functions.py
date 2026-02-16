import os
from pages.intelligence import get_persona_reports, get_spatial_insights
from dotenv import load_dotenv

load_dotenv(".env.local")

def test_intel():
    print("Testing get_persona_reports()...")
    reports = get_persona_reports()
    print(f"Reports found: {len(reports)}")
    for r in reports:
        print(f" - {r[0]}: {r[1]}")

    print("\nTesting get_spatial_insights()...")
    insights = get_spatial_insights()
    print(f"Insights found: {len(insights)}")
    for i in insights:
        print(f" - {i[0]}: {i[1][:50]}...")

if __name__ == "__main__":
    test_intel()
