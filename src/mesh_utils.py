import os
import requests
from dotenv import load_dotenv
import json
import streamlit as st
CACHE_FILE = "cache/umls_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            print("⚠️ Cache file exists but is empty or malformed. Resetting...")
            return {}
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)




load_dotenv()
UMLS_API_KEY = st.secrets["UMLS_API_KEY"]

# Auth helpers
def get_umls_tgt():
    auth_endpoint = "https://utslogin.nlm.nih.gov/cas/v1/api-key"
    resp = requests.post(auth_endpoint, data={"apikey": UMLS_API_KEY})
    if resp.status_code != 201:
        raise Exception("UMLS TGT request failed.")
    return resp.headers["location"]

def get_service_ticket(tgt_url):
    st_resp = requests.post(tgt_url, data={"service": "http://umlsks.nlm.nih.gov"})
    if st_resp.status_code != 200:
        raise Exception("UMLS service ticket request failed.")
    return st_resp.text

# Validate a term is MeSH via search
def is_mesh_term(term, tgt_url):
    ticket = get_service_ticket(tgt_url)
    search_url = "https://uts-ws.nlm.nih.gov/rest/search/current"
    params = {
        "string": term,
        "ticket": ticket,
        "pageSize": 5
    }
    resp = requests.get(search_url, params=params)
    if resp.status_code != 200:
        return False

    results = resp.json().get("result", {}).get("results", [])
    return any(item["rootSource"] == "MSH" for item in results)

# Validate entire categorized group
def validate_mesh_terms_via_umls(grouped_json):
    tgt_url = get_umls_tgt()
    cache = load_cache()
    updated_cache = cache.copy()
    validated = {}

    for category in ["interventions", "outcomes", "conditions"]:
        validated[category] = []
        for item in grouped_json.get(category, []):
            term = item["term"]
            if term in cache:
                is_valid = cache[term]
            else:
                is_valid = is_mesh_term(term, tgt_url)
                updated_cache[term] = is_valid

            if is_valid:
                validated[category].append(item)
            else:
                print(f"⚠️ Skipped (not MeSH): {term}")

    save_cache(updated_cache)
    return validated


def group_to_block(group, operator="OR"):
    if not group:
        return ""

    def format_term(item):
        term = item["term"]
        tag = item.get("tag", "").strip()
        if tag:
            return f'"{term}" {tag}'
        else:
            return f'"{term}"'

    return "(" + f" {operator} ".join([format_term(item) for item in group]) + ")"



def generate_final_query(validated_json):
    blocks = []
    for key in ["interventions", "outcomes", "conditions"]:
        block = group_to_block(validated_json.get(key, []))
        if block:
            blocks.append(block)
    return " AND ".join(blocks)

def validate_and_correct_tags(concepts_dict: dict) -> dict:
    """
    Wrapper for LangGraph agent that uses UMLS to validate MeSH terms.
    Invalid terms are dropped; tags are preserved from input.
    """
    return validate_mesh_terms_via_umls(concepts_dict)
