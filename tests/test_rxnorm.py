from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from models.db_models import User, Drug, DrugInteraction, DrugLog


# ─── resolve_drug tests ──────────────────────────────────────


def test_resolve_drug_exact_match(client, auth_header, db_session):
    """If the name already exists in the DB, return the Drug without calling RxNorm."""
    db_session.add(Drug(id="D100", name="Aspirin"))
    db_session.commit()

    from rxnorm import resolve_drug

    with patch("rxnorm.get_rxcui") as mock_rxcui:
        result = resolve_drug("Aspirin", db_session)
        assert result is not None
        assert result.id == "D100"
        assert result.name == "Aspirin"
        mock_rxcui.assert_not_called()


def test_resolve_drug_via_synonym(client, auth_header, db_session):
    """A synonym should resolve to the canonical Drug record via RxNorm lookup."""
    db_session.add(Drug(id="D100", name="Aspirin"))
    db_session.commit()

    from rxnorm import resolve_drug

    with patch("rxnorm.get_rxcui", return_value="1191") as mock_rxcui, \
         patch("rxnorm.get_drug_names", return_value=["acetylsalicylic acid", "Aspirin", "ASA"]) as mock_names:
        result = resolve_drug("acetylsalicylic acid", db_session)
        assert result is not None
        assert result.id == "D100"
        assert result.name == "Aspirin"
        mock_rxcui.assert_called_once_with("acetylsalicylic acid")
        mock_names.assert_called_once_with("1191")


def test_resolve_drug_no_rxcui(client, auth_header, db_session):
    """If RxNorm doesn't recognise the name, return None."""
    from rxnorm import resolve_drug

    with patch("rxnorm.get_rxcui", return_value=None):
        result = resolve_drug("UnknownDrug123", db_session)
        assert result is None


def test_resolve_drug_no_db_match(client, auth_header, db_session):
    """If RxNorm returns synonyms but none are in the DB, return None."""
    from rxnorm import resolve_drug

    with patch("rxnorm.get_rxcui", return_value="9999"), \
         patch("rxnorm.get_drug_names", return_value=["SomeName", "AnotherName"]):
        result = resolve_drug("WeirdDrug", db_session)
        assert result is None


# ─── Integration with drug logging ──────────────────────────────────


def test_log_drug_with_synonym_resolves_to_id(client, auth_header, db_session):
    """Logging a drug under a synonym should store the canonical drug_id."""
    user = db_session.query(User).filter_by(username="testuser").first()
    db_session.add(Drug(id="D100", name="Aspirin"))
    db_session.commit()

    mock_drug = MagicMock()
    mock_drug.id = "D100"
    mock_drug.name = "Aspirin"

    with patch("routers.drug_log_router.resolve_drug", return_value=mock_drug):
        response = client.post(
            "/drug-logs/",
            json={
                "drug_name": "acetylsalicylic acid",
                "dosage": "500mg",
                "datetime": datetime.utcnow().isoformat(),
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["drug_id"] == "D100"
        assert data["drug_name"] == "Aspirin"


# ─── Integration with interactions ───────────────────────────────────


def test_interactions_with_drug_id(client, auth_header, db_session):
    """Interactions should work using drug_id FK directly."""
    user = db_session.query(User).filter_by(username="testuser").first()

    d1 = Drug(id="D001", name="DrugA")
    d2 = Drug(id="D002", name="DrugB")
    db_session.add_all([d1, d2])
    db_session.add(DrugInteraction(drug_a_id="D001", drug_b_id="D002", level="major", category="A"))

    now = datetime.utcnow()
    db_session.add(DrugLog(user_id=user.id, drug_id="D001", dosage="10mg", datetime=now - timedelta(hours=2)))
    db_session.add(DrugLog(user_id=user.id, drug_id="D002", dosage="20mg", datetime=now - timedelta(hours=3)))
    db_session.commit()

    response = client.get("/interactions/major", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["drug_a"] == "DrugA"
    assert data[0]["drug_b"] == "DrugB"

def test_resolve_aspirin_to_acetylsalicylic_acid(client, auth_header, db_session):
    """Verify the specific case the user reported."""
    db_session.add(Drug(id="DDInter20", name="Acetylsalicylic acid", rxcui="1191"))
    db_session.commit()

    from rxnorm import resolve_drug
    result = resolve_drug("Aspirin", db_session)
    assert result is not None
    assert result.name == "Acetylsalicylic acid"
    assert result.rxcui == "1191"

