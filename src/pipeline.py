from src.llm_utils import categorize_user_query
from src.mesh_utils import validate_mesh_terms_via_umls, generate_final_query
from src.pubmed_utils import run_pubmed_search

def run_pipeline(user_query: str):
    print(f"🔍 User Query: {user_query}")

    raw_categorized = categorize_user_query(user_query)
    print(f"📦 LLM Output: {raw_categorized}")

    validated = validate_mesh_terms_via_umls(raw_categorized)
    print(f"✅ Validated MeSH Terms: {validated}")

    pubmed_query = generate_final_query(validated)
    print(f"🔎 PubMed Query: {pubmed_query}")

    return run_pubmed_search(pubmed_query)
