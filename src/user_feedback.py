#from src.followup_handler import answer_from_context
from sentence_transformers import SentenceTransformer, util

#model = SentenceTransformer("all-MiniLM-L6-v2")
#model = SentenceTransformer("cambridgeltl/biomed_roberta_base-sapbert-nli")
#model = SentenceTransformer("pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb")

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_user_feedback(results: list, user_query: str) -> str:
    print("\n What would you like to do next?")
    print("1. I’m satisfied — continue")
    print("2. Add/refine keywords")
    print("3. Analyze semantic similarity of results to a sentence")
    
    choice = input("Enter option (1/2/3): ").strip()
    return choice

def prompt_semantic_reference(user_query: str) -> str:
    print("\n To compute semantic similarity, please choose:")
    print("1. Use the original search query")
    print("2. Enter a new sentence for comparison")
    
    choice = input("Enter option (1/2): ").strip()

    if choice == "1":
        return user_query
    elif choice == "2":
        return input(" Enter your reference sentence: ").strip()
    else:
        print(" Invalid input. Defaulting to original query.")
        return user_query

def compute_semantic_scores(results, reference_text, excel_df=None):
    from sentence_transformers import SentenceTransformer, util
    #model = SentenceTransformer("all-MiniLM-L6-v2")
    model = SentenceTransformer("pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb")
    query_embedding = model.encode(reference_text, convert_to_tensor=True)

    # Build DOI → inclusion status map
    inclusion_map = {}
    if excel_df is not None:
        for _, row in excel_df.iterrows():
            doi = str(row.get("DOI", "")).strip().lower()
            status = str(row.get("Included/ Excluded", "")).strip().lower()
            inclusion_map[doi] = status

    included = []
    excluded = []

    for r in results:
        doi = (r.get("doi") or "").strip().lower()
        abstract = r.get("abstract", "")
        if not doi or not abstract:
            continue

        abstract_embedding = model.encode(abstract, convert_to_tensor=True)
        score = util.cos_sim(query_embedding, abstract_embedding).item()
        title = r.get("title", "")
        pmid = r.get("pmid", "")

        if inclusion_map.get(doi, "") == "included":
            included.append((doi, score, title, pmid))
        else:
            excluded.append((doi, score, title, pmid))

    # Sort both by descending score
    included.sort(key=lambda x: x[1], reverse=True)
    excluded.sort(key=lambda x: x[1], reverse=True)

    return included, excluded



