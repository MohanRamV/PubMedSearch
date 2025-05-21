from src.llm_utils import model
import json

def classify_followup(previous_query: str, user_input: str) -> str:
    prompt = f"""
User previously searched:
"{previous_query}"

Now they ask:
"{user_input}"

Classify this as:
a) New search
b) Refinement of previous search
c) A question about the previous results

Return only one of the letters: a, b, or c
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip().lower()[0]
    except Exception as e:
        print(f"❌ Follow-up intent classification failed: {e}")
        return "a"  # fallback

def answer_from_context(user_input: str, results: list) -> str:
    articles = "\n\n".join([
        f"{r['title']}\n{r.get('abstract', '')}" for r in results
    ][:5])  # use top 5 for brevity

    prompt = f"""
Given these biomedical research article summaries:

{articles}

Answer this user question:
"{user_input}"
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Failed to answer from context: {e}"
