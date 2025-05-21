'''
from src.mesh_utils import validate_and_correct_tags

def validate_tags(state: dict) -> dict:
    """
    Validates and corrects tags (like [Mesh], [Majr], [Publication Type]) for each concept group.
    Uses UMLS or internal rules to fix incorrect or vague tags.
    """
    extracted = state.get("extracted_concepts", {})

    try:
        validated = validate_and_correct_tags(extracted)
        print(f"✅ Validated tags: {validated}")
        return {**state, "validated_concepts": validated}
    except Exception as e:
        print(f"❌ Error in validate_tags: {e}")
        return {**state, "validated_concepts": {}}
'''