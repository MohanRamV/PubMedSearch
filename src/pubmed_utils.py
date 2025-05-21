# src/pubmed_utils.py

import os
import requests
from dotenv import load_dotenv
from xml.etree import ElementTree as ET

load_dotenv()
NCBI_API_KEY = os.getenv("NCBI_API_KEY")

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
'''
def run_pubmed_search(query: str, max_results: int = 500):
    """
    Performs a PubMed search using Entrez API and returns basic article details.

    Returns: List of dicts: {pmid, title}
    """

    # Step 1: Search PubMed (esearch)
    search_url = f"{BASE_URL}esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "api_key": NCBI_API_KEY
    }

    search_response = requests.get(search_url, params=search_params)
    search_data = search_response.json()
    id_list = search_data.get("esearchresult", {}).get("idlist", [])

    if not id_list:
        return []

    # Step 2: Fetch Article Summaries (esummary)
    summary_url = f"{BASE_URL}esummary.fcgi"
    summary_params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "json",
        "api_key": NCBI_API_KEY
    }

    summary_response = requests.get(summary_url, params=summary_params)
    summary_data = summary_response.json()

    results = []
    for pmid in id_list:
        doc = summary_data.get("result", {}).get(pmid, {})
        title = doc.get("title", "No title found")
        results.append({
            "pmid": pmid,
            "title": title
        })

    return results
'''
import xml.etree.ElementTree as ET

def run_pubmed_search(query: str, max_results: int = 500):
    try:
        # Step 1: Search PubMed
        search_url = f"{BASE_URL}esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance",
            "api_key": NCBI_API_KEY
        }
        search_response = requests.get(search_url, params=search_params)
        search_response.raise_for_status()  # catch 4xx/5xx errors
        search_data = search_response.json()
        id_list = search_data.get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return []

    except Exception as e:
        raise RuntimeError(f"[run_pubmed_search → esearch] failed: {e}")

    try:
        # Step 2: Get titles
        summary_url = f"{BASE_URL}esummary.fcgi"
        summary_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "json",
            "api_key": NCBI_API_KEY
        }
#        summary_response = requests.get(summary_url, params=summary_params)
        summary_response = requests.post(summary_url, data=summary_params)
        summary_response.raise_for_status()
        summary_data = summary_response.json()
    except Exception as e:
        raise RuntimeError(f"[run_pubmed_search → esummary] failed: {e}")

    try:
        # Step 3: Get DOIs
        fetch_url = f"{BASE_URL}efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "xml",
            "api_key": NCBI_API_KEY
        }
        #fetch_response = requests.get(fetch_url, params=fetch_params)
        fetch_response = requests.post(fetch_url, data=fetch_params)
        fetch_response.raise_for_status()
        root = ET.fromstring(fetch_response.text)

        doi_map = {}
        for article in root.findall(".//PubmedArticle"):
            pmid = article.findtext(".//PMID")
            doi = None
            abstract = ""
            abstract_elems = article.findall(".//AbstractText")
            if abstract_elems:
                abstract = " ".join(elem.text.strip() for elem in abstract_elems if elem.text)

            for id_elem in article.findall(".//ArticleId"):
                if id_elem.attrib.get("IdType") == "doi":
                    doi = id_elem.text
                    break
            if pmid:
                #print(f"📌 PMID {pmid} → DOI: {doi}")
                doi_map[pmid] = {
                    "doi": doi,
                    "abstract": abstract
                }
            

    except Exception as e:
        raise RuntimeError(f"[run_pubmed_search → efetch] failed: {e}")

    # Step 4: Assemble final results
    try:
        results = []
        for pmid in id_list:
            doc = summary_data.get("result", {}).get(pmid, {})
            title = doc.get("title", "No title found")
            doi_info = doi_map.get(pmid, {})
            results.append({
                "pmid": pmid,
                "title": title,
                "doi": doi_info.get("doi", "N/A"),
                "abstract": doi_info.get("abstract", "")
            })


        return results
    except Exception as e:
        raise RuntimeError(f"[run_pubmed_search → results assembly] failed: {e}")

def build_pubmed_query(concepts_dict: dict) -> str:
    """
    Constructs a Boolean PubMed query from categorized, validated terms.
    """
    def group_to_block(group, operator="OR"):
        if not group:
            return ""
        parts = []
        for item in group:
            term = item["term"]
            tag = item.get("tag", "")
            if tag:
                parts.append(f'"{term}" {tag}')
            else:
                parts.append(f'"{term}"')
        return f"({f' {operator} '.join(parts)})"

    blocks = []
    for category in ["interventions", "outcomes", "conditions"]:
        block = group_to_block(concepts_dict.get(category, []))
        if block:
            blocks.append(block)

    return " AND ".join(blocks) if blocks else ""
