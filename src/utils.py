import json
import ast
import re
import pandas as pd


def load_excel_dois(excel_path: str) -> set:
    try:
        df = pd.read_excel(excel_path, engine="openpyxl")
        print("📋 Excel Columns:", list(df.columns))  # Debug

        # Normalize column names
        df.columns = df.columns.str.strip()

        # Use exact column name with space
        included_dois = df[
            df["Included/ Excluded"].str.strip().str.lower() == "included"
        ]["DOI"]

        return set(str(doi).strip().lower() for doi in included_dois.dropna())

    except Exception as e:
        print(f"❌ Failed to load included DOIs from Excel: {e}")
        return set()



def safe_parse_llm_response(response_text: str) -> dict:
    """
    Safely parse an LLM (e.g., Gemini) response into a Python dict.
    Handles JSON, Python-style dicts, and removes code fences if present.
    """
    if not response_text or not isinstance(response_text, str):
        return {}

    # Step 1: Remove ```json or ``` at beginning and end
    cleaned = response_text.strip()

    # Remove starting ```json or ```
    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)

    # Remove trailing ```
    cleaned = re.sub(r'\s*```$', '', cleaned)

    # Step 2: Try parsing as JSON
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Step 3: Try parsing as Python dict (fallback)
    try:
        return ast.literal_eval(cleaned)
    except Exception as e:
        print("❌ Failed to parse Gemini response.")
        print("🔎 Cleaned content:\n", cleaned)
        return {}
