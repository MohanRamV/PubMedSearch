from src.llm_utils import refine_user_query

def refine_query(state: dict) -> dict:
    """
    Uses LLM to rewrite or expand the user query based on poor search results.
    Returns an updated user query in the state for the next search cycle.
    """
    original_query = state.get("user_query", "")
    previous_results = state.get("search_results", [])

    try:
        new_query = refine_user_query(original_query, previous_results)
        print(f"🔁 Refined Query:\n{new_query}")
        return {**state, "user_query": new_query}
    except Exception as e:
        print(f"❌ Error in refine_query: {e}")
        return {**state, "user_query": original_query}  # fallback to original
