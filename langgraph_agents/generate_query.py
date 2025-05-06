from src.pubmed_utils import build_pubmed_query

def generate_query(state: dict) -> dict:
    """
    Converts validated concepts into a structured PubMed Boolean search query.
    """
    concepts = state.get("validated_concepts", {})

    try:
        query = build_pubmed_query(concepts)
        print(f"🧾 Generated PubMed Query:\n{query}")
        return {**state, "query": query}
    except Exception as e:
        print(f"❌ Error in generate_query: {e}")
        return {**state, "query": ""}
