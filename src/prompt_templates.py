# src/prompt_templates.py

# Prompt for query reformulation
LLM_CLEAN_QUERY_PROMPT = """
You are an expert biomedical researcher. Rephrase the following user query to be more structured
and aligned with PubMed keyword or MeSH-based search strategy. Return only the rephrased query.

Original Query:
"{query}"
"""

# Prompt for keyword suggestions (if you expand later)
LLM_KEYWORD_SUGGESTION_PROMPT = """
Given the following medical research query, extract key biomedical terms (diseases, drugs, outcomes)
and map them to PubMed-friendly keywords. Return them as a comma-separated list.

Query:
"{query}"
"""

CATEGORIZATION_PROMPT = """
You are a biomedical NLP assistant helping to build PubMed search queries.

Given the following user query:
"{query}"
First find if the user has already provided structured search terms or a search query. If they have, validate and correct typos and paranthesis only if required.
Else If, extract structured search terms from the query. The user may have provided some terms in a free-text format, but they are not structured.
Else, your task is to extract structured search terms in the following 3 categories:
1. **Interventions or Drug Classes**
   - Examples: drug names, mechanisms, receptor agonists
   - Tags: [Mesh], [Majr], [Pharmacological Action], [Supplementary Concept]

2. **Outcomes or Study Designs**
   - Examples: trial phases, treatment outcomes, therapeutic use
   - Tags: [Mesh], [Publication Type], or leave blank if none

3. **Conditions or Disorders**
   - Examples: psychiatric, cognitive, neurodevelopmental, or DSM-related terms
   - Tags: [Mesh], [Majr]

Please return:
- At least 2–3 items per category, even if inferred
- Only valid PubMed search tags (avoid invented ones)
- Exact matches for tags like:
  - "Clinical Trial, Phase I" [Publication Type]
  - "Treatment Outcome" [Mesh]
  - "Mental Disorders" [Mesh]

If you're unsure of a tag, leave it blank.

Output format: Valid JSON only, no markdown or explanation. Use double quotes.

Example format:
{{
  "interventions": [{{"term": "GLP-1 receptor agonists", "tag": "[Pharmacological Action]"}}],
  "outcomes": [{{"term": "Treatment Outcome", "tag": "[Mesh]"}}, {{"term": "Clinical Trial, Phase II", "tag": "[Publication Type]"}}],
  "conditions": [{{"term": "Mental Disorders", "tag": "[Mesh]"}}]
}}
"""





