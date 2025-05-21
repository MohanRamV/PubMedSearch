import streamlit as st
import pandas as pd
from src.utils import load_excel_dois
from langgraph_pubmed import graph
from src.run_embase_search import run_embase_search
from src.user_feedback import compute_semantic_scores, prompt_semantic_reference
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # Avoid Intel OpenMP issues
os.environ["STREAMLIT_WATCH_USE_POLLING"] = "true"  # Disable problematic file watching

# ---- Init state variables
for key in ["user_query", "excel_path", "final_state", "semantic_mode", "semantic_scores", "trigger_rerun"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ---- App Title
st.markdown("""
<div style='background: linear-gradient(to right, #1d976c, #93f9b9); 
            padding: 20px; border-radius: 10px; text-align:center; color:white;'>
    <h1> PubMed Search Engine</h1>
</div>
""", unsafe_allow_html=True)


# ---- Input Form
with st.form("search_form"):
    user_query = st.text_input("Enter your biomedical search query:")
    #excel_path = st.text_input("Excel file path with DOIs", "data/GLP-1 RA Abstracts Sorting file.xlsx")
    #excel_path = "data/GLP-1 RA Abstracts Sorting file.xlsx"
    excel_path = st.file_uploader("Upload an Excel file with DOIs", type=["xlsx"])

    if excel_path:
        st.session_state.excel_path = excel_path
    else:
        excel_path = "data/GLP-1 RA Abstracts Sorting file.xlsx"
        st.markdown("Taken Default Excel file: GLP-1 RA Abstracts Sorting file.xlsx")
        st.session_state.excel_path = excel_path
        

    submitted = st.form_submit_button("Run Search")

    if submitted:
        st.session_state.user_query = user_query
        st.session_state.excel_path = excel_path
        st.session_state.semantic_mode = False
        st.session_state.semantic_scores = None

        with st.spinner("Running LangGraph pipeline..."):
            excel_dois = load_excel_dois(excel_path)
            initial_state = {
                "user_query": user_query,
                "excel_dois": excel_dois
            }
            st.session_state.final_state = graph.invoke(initial_state, config={"recursion_limit": 5})
    # After rerun redirect, reset trigger flag
    if st.session_state.trigger_rerun:
        st.session_state.trigger_rerun = None


# ---- Display Results
if st.session_state.final_state:
    final_state = st.session_state.final_state
    results = final_state.get("search_results", [])
    pubmed_query = final_state.get("query", "")
    #embase_query = final_state.get("embase_query", "")
    user_query = st.session_state.user_query

    st.markdown("""
    <div style='background: #f7f7f7; padding: 15px; border-left: 5px solid #28a745; border-radius: 5px;'>
        <h4 style='color:#28a745;'> Generated PubMed Query</h4>
    </div>
    """, unsafe_allow_html=True)
    st.text_area("", pubmed_query, height=100)

    #st.text_area("Embase Query", embase_query, height=100)

    # ---- Show Results (Only if not semantic mode)
    if not st.session_state.semantic_mode:
        st.markdown(
            "<h3 style='font-size:26px; color:#28a745;'> Top PubMed Search Results</h3>",
            unsafe_allow_html=True
        )

        with st.expander("Click to expand results", expanded=True):
            for i, r in enumerate(results, start=1):    
                st.markdown(f"""
                    <div style="background-color:#e6f2ff; padding:10px; margin:10px 0; border-left: 4px solid #007acc; border-radius: 5px;">
                        <b>{i}. {r['title']}</b><br>
                        <span><b>DOI:</b> <code>{r['doi']}</code></span><br>
                        <a href="https://pubmed.ncbi.nlm.nih.gov/{r['pmid']}/" target="_blank">🔗 PMID {r['pmid']}</a>
                    </div>
                    """, unsafe_allow_html=True)


        # ---- Matched DOIs
        excel_dois = load_excel_dois(st.session_state.excel_path)
        pubmed_dois = {r["doi"].strip().lower() for r in results if r.get("doi")}
        matched_dois = pubmed_dois.intersection(excel_dois)
        st.success(f" DOIs that are Included in Excel from PubMed: {len(matched_dois)} / {len(pubmed_dois)}")

        #embase_results = run_embase_search(embase_query)
        #embase_dois = {r["doi"].strip().lower() for r in embase_results if r.get("doi")}
        #matched_embase_dois = embase_dois.intersection(excel_dois)
        #st.info(f" Matched DOIs in Embase: {len(matched_embase_dois)} / {len(embase_dois)}")

        # ---- Feedback Options
        choice = st.radio("What would you like to do next?", [" Select what do you want next!", " Refine Query", " Get Semantic Scores"])

        if choice == " Refine Query":
            # Clear previous result and trigger rerun
            st.session_state.final_state = None
            st.session_state.semantic_mode = False
            st.session_state.trigger_rerun = True
            st.rerun()


        elif choice == " Get Semantic Scores":
            st.session_state.semantic_mode = True

# ---- Semantic Similarity View
if st.session_state.semantic_mode:
    st.markdown("""
        <div style='background: linear-gradient(to right, #654ea3, #eaafc8); 
                    padding: 15px; border-radius: 8px; text-align:center; color:white;'>
            <h2> Semantic Similarity Matching</h2>
        </div>
        """, unsafe_allow_html=True)


    st.markdown("<br><b style='color:#6c757d;'> Choose your reference for semantic comparison:</b>", unsafe_allow_html=True)
    choice = st.radio("", ["Use original search query", "Enter new sentence for semantic comparison"])

    if choice == "Use original search query":
        ref_text = st.session_state.user_query
    else:
        ref_text = st.text_input(" Enter a new reference sentence for semantic comparison:")

    if ref_text:
        excel_df = pd.read_excel(st.session_state.excel_path)
        included_scores, excluded_scores = compute_semantic_scores(results, ref_text, excel_df)

        st.session_state.semantic_scores = (included_scores, excluded_scores)


    if st.session_state.semantic_scores:
        included_scores, excluded_scores = st.session_state.semantic_scores
        #included = [s for s in scores if s[3] is True]
        #excluded = [s for s in scores if s[3] is not True]

        st.markdown("""
        <div style='background: linear-gradient(to right, #d9f9d9, #bce0fd); 
                    padding: 10px; border-radius: 6px; color: #1d3557;'>
            <h4> Semantic Scores (Included in Excel)</h4>
        </div>
        """, unsafe_allow_html=True)



        with st.expander("Click to expand results", expanded=True):
            for i, (doi, score, title, pmid) in enumerate(included_scores, start=1):
                st.markdown(f"""
                <div style='background-color:#f0fff4; padding:12px; margin:10px 0; 
                            border-left:4px solid #5cb85c; border-radius:6px; box-shadow: 1px 1px 5px rgba(0,0,0,0.05);'>
                <b>{i}. {title}</b><br>
                <b>DOI:</b> <code>{doi}</code><br>
                <b>Score:</b> {score:.4f}<br>
                <a href="https://pubmed.ncbi.nlm.nih.gov/{pmid}/" target="_blank">🔗 PMID {pmid}</a>
                </div>
                """, unsafe_allow_html=True)


                if pmid:
                    st.markdown(f" **PMID**: [{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)")
                st.markdown("---")


        st.markdown("""
            <div style='background: linear-gradient(to right, #fceabb, #f8b500); 
                        padding: 10px; border-radius: 6px; color: #333333;'>
                <h4> Semantic Scores (Excluded or Not Marked)</h4>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("Click to expand results", expanded=True):
        
            for i, (doi, score, title, pmid) in enumerate(excluded_scores, start=len(included_scores) + 1):
                st.markdown(f"""
                <div style='background-color:#fff9e6; padding:10px; margin:8px 0; 
                            border-left:4px solid #f0ad4e; border-radius:5px;'>
                <b>{i}. {title}</b><br>
                <b>DOI:</b> <code>{doi}</code><br>
                <b>Score:</b> {score:.4f}<br>
                <a href="https://pubmed.ncbi.nlm.nih.gov/{pmid}/" target="_blank">🔗 PMID {pmid}</a>
                </div>
                """, unsafe_allow_html=True)


                if pmid:
                    st.markdown(f" **PMID**: [{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)")
                st.markdown("---")

        from sklearn.metrics import roc_auc_score
        import matplotlib.pyplot as plt

        # ------------------ Combine and label all scored entries ------------------
        # Format: (doi, score, title, pmid, is_included)
        labeled_included = [(doi, score, title, pmid, True) for doi, score, title, pmid in included_scores]
        labeled_excluded = [(doi, score, title, pmid, False) for doi, score, title, pmid in excluded_scores]

        all_scored = labeled_included + labeled_excluded
        all_scored.sort(key=lambda x: x[1], reverse=True)  # Sort by score descending

        # ------------------ Precision@k and Recall@k ------------------
        top_k = 30
        top_k_subset = all_scored[:top_k]
        true_positives = [r for r in top_k_subset if r[4] is True]

        precision_at_k = len(true_positives) / top_k
        total_included = len(labeled_included)
        recall_at_k = len(true_positives) / total_included if total_included else 0

        # ------------------ ROC AUC ------------------
        y_true = [1 if r[4] else 0 for r in all_scored]
        y_scores = [r[1] for r in all_scored]
        auc = roc_auc_score(y_true, y_scores)

        # ------------------ Streamlit Display ------------------
        st.subheader(" Semantic Matching Accuracy Metrics")
        st.markdown(f"""
            <div style='display: flex; gap: 30px;'>
                <div style='background:#e0f7e9; padding:10px; border-radius:8px; width:30%; text-align:center;'>
                    <b>ROC AUC</b><br><span style='font-size:20px'>{auc:.3f}</span>
                </div>
                <div style='background:#fff3cd; padding:10px; border-radius:8px; width:30%; text-align:center;'>
                    <b>Precision@{top_k}</b><br><span style='font-size:20px'>{precision_at_k:.2f}</span>
                </div>
                <div style='background:#f8d7da; padding:10px; border-radius:8px; width:30%; text-align:center;'>
                    <b>Recall@{top_k}</b><br><span style='font-size:20px'>{recall_at_k:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


        # ------------------ Score Distributions ------------------
        included_only_scores = [s[1] for s in labeled_included]
        excluded_only_scores = [s[1] for s in labeled_excluded]

        st.subheader(" Semantic Score Distribution")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(included_only_scores, bins=15, alpha=0.6, label="Included", density=True)
        ax.hist(excluded_only_scores, bins=15, alpha=0.6, label="Excluded", density=True)
        ax.set_xlabel("Semantic Similarity Score")
        ax.set_ylabel("Density")
        ax.set_title("Semantic Score Histogram")
        ax.legend()
        st.pyplot(fig)






