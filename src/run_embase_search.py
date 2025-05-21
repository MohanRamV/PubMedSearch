import os
import requests
from dotenv import load_dotenv
import streamlit as st
load_dotenv()
EMBASE_API_KEY = st.secrets["EMBASE_API_KEY"]
EMBASE_BASE_URL = st.secrets["EMBASE_BASE_URL"]  # Adjust if different

HEADERS = {
    "Accept": "application/json",
    "X-ELS-APIKey": EMBASE_API_KEY
}


def run_embase_search(query: str, max_results: int = 100) -> list:
    """
    Search Embase using Elsevier API and return article metadata.
    """
    if not query.strip():
        print("⚠️ Skipping Embase search: Query is empty.")
        return []

    print(f"📡 Running Embase search...")
    
    params = {
        "query": query,
        "count": max_results
    }

    try:
        response = requests.get(EMBASE_BASE_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        entries = data.get("search-results", {}).get("entry", [])
        for item in entries:
            doi = item.get("prism:doi", None)
            title = item.get("dc:title", "No title")
            abstract = item.get("dc:description", "")  # Embase may store abstract here

            results.append({
                "title": title,
                "doi": doi,
                "abstract": abstract
            })

        print(f"✅ Retrieved {len(results)} Embase articles")
        return results

    except Exception as e:
        print(f"❌ Error in Embase API call: {e}")
        return []
