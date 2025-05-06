from src.llm_utils import categorize_user_query

def extract_concepts(state: dict) -> dict:
    """
    LLM-powered concept extractor from user query.
    """
    user_query = state.get("user_query", "")
    print(f"🧠 Extracting concepts from user query: {user_query}")

    try:
        extracted = categorize_user_query(user_query)
        return {**state, "extracted_concepts": extracted}
        
    except Exception as e:
        print(f"❌ Error in extract_concepts: {e}")
        return {**state, "extracted_concepts": {}}
