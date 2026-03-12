from datetime import datetime, timedelta
from models.db_models import User, Drug, DrugInteraction, DrugLog

def seed_data(db_session, user_id):
    # Add drugs
    d1 = Drug(id="D001", name="DrugA")
    d2 = Drug(id="D002", name="DrugB")
    d3 = Drug(id="D003", name="DrugC")
    d4 = Drug(id="D004", name="DrugD")
    db_session.add_all([d1, d2, d3, d4])
    
    # Add interactions
    # Major: A and B
    i1 = DrugInteraction(drug_a_id="D001", drug_b_id="D002", level="major", category="A")
    # Moderate: A and D (D is old)
    i2 = DrugInteraction(drug_a_id="D001", drug_b_id="D004", level="moderate", category="B")
    # Minor: B and C
    i3 = DrugInteraction(drug_a_id="D002", drug_b_id="D003", level="minor", category="C")
    db_session.add_all([i1, i2, i3])
    
    # Add logs (using drug_id instead of drug_name)
    now = datetime.utcnow()
    l1 = DrugLog(user_id=user_id, drug_id="D001", dosage="10mg", datetime=now - timedelta(hours=2))
    l2 = DrugLog(user_id=user_id, drug_id="D002", dosage="20mg", datetime=now - timedelta(hours=10))
    l3 = DrugLog(user_id=user_id, drug_id="D003", dosage="30mg", datetime=now - timedelta(hours=5))
    l4 = DrugLog(user_id=user_id, drug_id="D004", dosage="40mg", datetime=now - timedelta(hours=48)) # old
    db_session.add_all([l1, l2, l3, l4])
    db_session.commit()

def test_get_major_interactions(client, auth_header, db_session):
    user = db_session.query(User).filter_by(username="testuser").first()
    seed_data(db_session, user.id)
    
    response = client.get("/interactions/major", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["drug_a"] == "DrugA"
    assert data[0]["drug_b"] == "DrugB"
    assert data[0]["level"].lower() == "major"

def test_get_moderate_interactions(client, auth_header, db_session):
    user = db_session.query(User).filter_by(username="testuser").first()
    seed_data(db_session, user.id)
    
    response = client.get("/interactions/moderate", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    # DrugD is older than 24h, so no moderate interactions should be returned
    assert len(data) == 0

def test_get_minor_interactions(client, auth_header, db_session):
    user = db_session.query(User).filter_by(username="testuser").first()
    seed_data(db_session, user.id)
    
    response = client.get("/interactions/minor", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "DrugB" in (data[0]["drug_a"], data[0]["drug_b"])
    assert "DrugC" in (data[0]["drug_a"], data[0]["drug_b"])

def test_get_safe_interactions(client, auth_header, db_session):
    user = db_session.query(User).filter_by(username="testuser").first()
    seed_data(db_session, user.id)
    
    response = client.get("/interactions/safe", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    # Recent drugs: DrugA, DrugB, DrugC
    # Pairs: (A, B) -> major, (B, C) -> minor.
    # Safe pairs should be (A, C)
    assert len(data) == 1
    assert data[0]["level"] == "safe"
    assert "DrugA" in (data[0]["drug_a"], data[0]["drug_b"])
    assert "DrugC" in (data[0]["drug_a"], data[0]["drug_b"])

def test_interactions_unauthenticated(client):
    response = client.get("/interactions/major")
    assert response.status_code == 401

from unittest.mock import patch, MagicMock

def test_ask_interaction(client, auth_header, db_session):
    user = db_session.query(User).filter_by(username="testuser").first()
    seed_data(db_session, user.id)
    
    with patch("routers.interaction_router.genai.Client") as mock_client:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a mock LLM response."
        mock_instance.models.generate_content.return_value = mock_response
        mock_client.return_value = mock_instance
        
        with patch.dict("os.environ", {"GEMINI_API_KEY": "fake_key"}):
            response = client.post(
                "/interactions/ask",
                headers=auth_header,
                json={"prompt": "Is it safe to take these?"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["answer"] == "This is a mock LLM response."
            mock_instance.models.generate_content.assert_called_once()
