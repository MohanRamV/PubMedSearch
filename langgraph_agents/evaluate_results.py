"""def evaluate_results(state: dict) -> dict:
    results = state.get("search_results", [])
    if len(results) < 3:
        print("⚠️ Too few results, marking as irrelevant.")
        return {**state, "branch_decision": "irrelevant"}

    print("✅ Results are relevant.")
    return {**state, "branch_decision": "relevant"}
"""
import pandas as pd
"""
def load_excel_dois(excel_path: str) -> set:
    df = pd.read_excel(excel_path, engine='openpyxl')
    return set(str(d).strip().lower() for d in df['DOI'].dropna())
"""

def evaluate_results(state: dict) -> dict:
    results = state.get("search_results", [])
    retry_count = state.get("retry_count", 0)
    excel_dois = state.get("excel_dois", set())

    pubmed_dois = set(
        r["doi"].strip().lower()
        for r in results if r.get("doi")
    )

    match_count = len(pubmed_dois.intersection(excel_dois))
    print(f"📊 Matched DOIs: {match_count} / {len(pubmed_dois)}")

    # 🔐 Add graceful stop condition
    if match_count >= 3:
        decision = "relevant"
    elif retry_count >= 3:
        print("⚠️ Max retry limit reached. Exiting.")
        decision = "exit"
    else:
        decision = "irrelevant"

    return {
        **state,
        "branch_decision": decision,
        "retry_count": retry_count + 1
    }

