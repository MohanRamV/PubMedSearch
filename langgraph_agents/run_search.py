from src.pubmed_utils import run_pubmed_search

def run_search(state: dict) -> dict:
    """
    Executes PubMed search using Entrez API and returns article results.
    """
    query = state.get("query", "")
    if not query:
        print("⚠️ No query found in state.")
        return {**state, "search_results": []}

    try:
        results = run_pubmed_search(query)
        print(f"📦 Retrieved {len(results)} PubMed results.")
        return {**state, "search_results": results}
    except Exception as e:
        print(f"❌ Error in run_search: {e}")
        return {**state, "search_results": []}
