from langgraph_agents.extract_concepts import extract_concepts
from langgraph_agents.validate_tags import validate_tags
from langgraph_agents.generate_query import generate_query
from langgraph_agents.run_search import run_search
from langgraph_agents.evaluate_results import evaluate_results
from langgraph_agents.refine_query import refine_query
from src.utils import load_excel_dois
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

# ... import all your agent functions ...

class PubMedState(TypedDict, total=False):
    user_query: str
    extracted_concepts: dict
    validated_concepts: dict
    query: str
    search_results: List[dict]

# ✅ Step 1: Initialize graph with schema
builder = StateGraph(PubMedState)

# ✅ Step 2: Add all nodes first
builder.add_node("extract_concepts", extract_concepts)
builder.add_node("validate_tags", validate_tags)
builder.add_node("generate_query", generate_query)
builder.add_node("run_search", run_search)
builder.add_node("evaluate_results", evaluate_results)
builder.add_node("refine_query", refine_query)

# ✅ Step 3: Set entry point and linear edges
builder.set_entry_point("extract_concepts")
builder.add_edge("extract_concepts", "validate_tags")
builder.add_edge("validate_tags", "generate_query")
builder.add_edge("generate_query", "run_search")
builder.add_edge("run_search", "evaluate_results")
builder.add_edge("refine_query", "extract_concepts")

def branching_router(state: PubMedState) -> str:
    return state.get("branch_decision", "irrelevant")


# ✅ Step 4: Add conditional edges LAST
builder.add_node("terminate", lambda state: state)  # dummy node to stop

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



# ✅ Step 5: Compile  for graph invocation
graph = builder.compile()

# 🟩 This part goes at the very bottom:
if __name__ == "__main__":
    user_query = input("🔍 Enter your biomedical query: ")
    initial_state = {"user_query": user_query}

    ###Evaluate With Excel DOIs###
    excel_path = "data/GLP-1 RA Abstracts Sorting file.xlsx"
    excel_dois = load_excel_dois(excel_path)

    initial_state = {
        "user_query": user_query,
        "excel_dois": excel_dois
    }

    print("\n🧠 Running LangGraph Biomedical Search...\n")
    final_state = graph.invoke(initial_state,config={"recursion_limit": 25}) #Just 5 recursions for now

    results = final_state.get("search_results", [])
    if not results:
        print("❌ No relevant articles found.")
    else:
        print(f"\n📄 Top {len(results)} PubMed Results:\n")
        for idx, result in enumerate(results, 1):
            print(f"{idx}. {result['title']}")
            print(f"   PMID: {result['pmid']}")
            print(f"   DOI: {result.get('doi', 'N/A')}")
            print(f"   🔗 https://pubmed.ncbi.nlm.nih.gov/{result['pmid']}/\n")
