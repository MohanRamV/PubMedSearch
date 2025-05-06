import pandas as pd

def load_excel_dois(filepath: str, column_name="DOI") -> set:
    df = pd.read_excel(filepath)
    dois = df[column_name].dropna().astype(str).str.strip().str.lower()
    return set(dois)

def extract_pipeline_dois(pipeline_results: list, key="doi") -> set:
    return {
        res[key].strip().lower()
        for res in pipeline_results
        if key in res and isinstance(res[key], str)
    }

def match_dois(excel_dois: set, result_dois: set):
    matched = result_dois & excel_dois
    missed = result_dois - matched
    return matched, missed

def evaluate_pipeline(excel_file: str, pipeline_results: list):
    excel_dois = load_excel_dois(excel_file)
    pipeline_dois = extract_pipeline_dois(pipeline_results)

    matched, missed = match_dois(excel_dois, pipeline_dois)

    print(f"📊 Total DOIs in Excel: {len(excel_dois)}")
    print(f"📡 DOIs from pipeline: {len(pipeline_dois)}")
    print(f"✅ Matched DOIs: {len(matched)}")
    print(f"❌ Missed DOIs: {len(missed)}")

    if missed:
        print("\n🚨 Sample missed DOIs:")
        for doi in list(missed)[:5]:
            print(f" - {doi}")
