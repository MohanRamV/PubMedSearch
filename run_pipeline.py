# run_pipeline.py

from src.pipeline import run_pipeline
from src.verify_matches import evaluate_pipeline

if __name__ == "__main__":
    print("🔍 PubMed Hybrid Search Engine: LLM + NER + MeSH\n")
    user_query = input("Enter your biomedical search query: ")
    
    try:
        results = run_pipeline(user_query)
        print("\n📄 Top PubMed Search Results:\n")
        for idx, result, doi in enumerate(results, 1):
            print(f"{idx}. {result['title']}")
            print(f"   PMID: {result['pmid']}")
            print(f"   URL: https://pubmed.ncbi.nlm.nih.gov/{result['pmid']}/\n")
            print(f"   DOI: {result['doi']}")
        
        # Evaluate the pipeline results against the Excel file
        evaluate_pipeline("D:\RA\PubMedEngine\data\GLP-1 RA Abstracts Sorting file.xlsx", results)
    except Exception as e:
        print(f"❌ Error running pipeline: {e}")





