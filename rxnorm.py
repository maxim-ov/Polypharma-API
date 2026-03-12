import httpx
from sqlalchemy.orm import Session
from models.db_models import Drug

def get_rxcui(drug_name: str) -> str | None:
    """Get the RxNorm Concept Unique Identifier (RxCUI) for a drug name."""
    url = "https://rxnav.nlm.nih.gov/REST/rxcui.json"
    params = {"name": drug_name, "search": 1}
    try:
        response = httpx.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        rxnorm_ids = data.get("idGroup", {}).get("rxnormId")
        if rxnorm_ids:
            return rxnorm_ids[0]
    except Exception:
        return None
    return None

def get_drug_names(rxcui: str) -> list[str]:
    """Get all known names and synonyms for a given RxCUI."""
    url = f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/allProperties.json"
    params = {"prop": "names"}
    try:
        response = httpx.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        prop_concepts = data.get("propConceptGroup", {}).get("propConcept", [])
        return [prop["propValue"] for prop in prop_concepts]
    except Exception:
        return []

def resolve_drug(drug_name: str, db: Session) -> Drug | None:
    """Resolve a user-entered drug name to a Drug record in the database.

    Resolution strategy:
    1. Direct name match (case-insensitive).
    2. Get RxCUI for input name and search DB by RxCUI (High Precision).
    3. Fallback: Get all synonyms from RxNorm and search DB by name (Breadth).
    """
    # 1. Direct name match
    exact = db.query(Drug).filter(Drug.name.ilike(drug_name)).first()
    if exact:
        return exact

    # 2. Get RxCUI and search by RxCUI
    rxcui = get_rxcui(drug_name)
    if rxcui:
        # Match by RxCUI indexed in the database during seeding
        rxcui_match = db.query(Drug).filter(Drug.rxcui == rxcui).first()
        if rxcui_match:
            return rxcui_match

        # 3. Fallback: Synonyms from RxNorm
        synonyms = get_drug_names(rxcui)
        for synonym in synonyms:
            syn_match = db.query(Drug).filter(Drug.name.ilike(synonym)).first()
            if syn_match:
                return syn_match

    return None
