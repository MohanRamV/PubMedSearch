from langgraph_agents.run_search import run_search
from langgraph_agents.evaluate_results import evaluate_results
from langgraph_agents.refine_query import refine_query
from src.llm_utils import categorize_user_query
from src.utils import load_excel_dois
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from sentence_transformers import SentenceTransformer, util
from src.llm_utils import categorize_user_query, generate_embase_query
from src.user_feedback import get_user_feedback, compute_semantic_scores,prompt_semantic_reference



# ✅ Define new simplified state
class PubMedState(TypedDict, total=False):
    user_query: str
    query: str
    embase_query: str
    search_results: List[dict]
    branch_decision: str
    retry_count: int
    excel_dois: set


# ✅ New direct LLM-based query generator


def generate_query(state: dict) -> dict:
    user_query = state.get("user_query", "")
    pubmed_query = categorize_user_query(user_query)
    embase_query = generate_embase_query(user_query)
    print(f"🧾 PubMed Query:\n{pubmed_query}")
    print(f"🧾 Embase Query:\n{embase_query}")
    return {**state, "query": pubmed_query, "embase_query": embase_query}



# ✅ Build LangGraph
builder = StateGraph(PubMedState)

builder.add_node("generate_query", generate_query)
builder.add_node("run_search", run_search)
builder.add_node("evaluate_results", evaluate_results)
builder.add_node("refine_query", refine_query)
builder.add_node("terminate", lambda state: state)

builder.set_entry_point("generate_query")
builder.add_edge("generate_query", "run_search")
builder.add_edge("run_search", "evaluate_results")
builder.add_edge("refine_query", "generate_query")


# ✅ Routing logic
def branching_router(state: PubMedState) -> str:
    return state.get("branch_decision", "irrelevant")


builder.add_conditional_edges(
    "evaluate_results",
    branching_router,
    {
        "relevant": END,
        "irrelevant": "refine_query",
        "exit": "terminate"
    }
)

builder.add_edge("terminate", END)

graph = builder.compile()


# ✅ Run it
if __name__ == "__main__":
    user_query = input("🔍 Enter your biomedical query: ")
    excel_path = "data/GLP-1 RA Abstracts Sorting file.xlsx"
    excel_dois = load_excel_dois(excel_path)

    initial_state = {
        "user_query": user_query,
        "excel_dois": excel_dois
    }

    print("\n🧠 Running LangGraph Biomedical Search...\n")
    final_state = graph.invoke(initial_state, config={"recursion_limit": 5})

    results = final_state.get("search_results", [])
    #print(results[:5])
    pipeline_dois = {r["doi"].strip().lower() for r in results if r.get("doi")}
    matched_dois = pipeline_dois.intersection(excel_dois)

    #print(f"✅ Matched DOIs: {len(matched_dois)} / {len(pipeline_dois)}")
    #####
    #Embase search
    """
    from src.run_embase_search import run_embase_search

    # Fetch Embase results
    embase_query = final_state.get("embase_query", "")
    embase_results = run_embase_search(embase_query)


    # Extract DOIs from Embase
    embase_dois = {r["doi"].strip().lower() for r in embase_results if r.get("doi")}
    matched_embase_dois = embase_dois.intersection(excel_dois)

    print(f"✅ Matched DOIs in Embase: {len(matched_embase_dois)} / {len(embase_dois)}")
    """
    #Follow-up handling

    choice = get_user_feedback(results, user_query)

    if choice == "1":
        print("✅ Great! You may now ask a follow-up question or exit.")
    elif choice == "2":
        user_query = input("✍️ Enter your refined query or keywords: ")
        # re-run graph with new user_query
    elif choice == "3":
    
        ref_text = prompt_semantic_reference(user_query)
        scores = compute_semantic_scores(results, ref_text)
        
        print("\n🔍 Top Semantic Matches:")
        for doi, score, title in scores:
            print(f"• Score: {score:.4f} | DOI: {doi}")
            print(f"  Title: {title}\n")





def run_graph_pipeline(user_query: str, excel_path: str) -> dict:
    excel_dois = load_excel_dois(excel_path)
    initial_state = {
        "user_query": user_query,
        "excel_dois": excel_dois
    }
    return graph.invoke(initial_state, config={"recursion_limit": 5})



"""

    # -------- Semantic scoring --------
    print("\n🧠 Running semantic similarity on matched abstracts...")

    model = SentenceTransformer("all-MiniLM-L6-v2")  # Small & fast

    query_embedding = model.encode(user_query, convert_to_tensor=True)

    semantic_results = []
    for r in results:
        doi = (r.get("doi") or "").strip().lower()
        if doi in matched_dois:
            abstract = r.get("abstract", "")
            if abstract:
                abstract_embedding = model.encode(abstract, convert_to_tensor=True)
                score = util.cos_sim(query_embedding, abstract_embedding).item()
                semantic_results.append((doi, score))


    # Sort by highest score
    semantic_results.sort(key=lambda x: x[1], reverse=True)

    print(f"\n📊 Semantic Scores for Matched DOIs:\n")
    for doi, score in semantic_results:
        print(f"- DOI: {doi} → Similarity Score: {score:.4f}")
        """