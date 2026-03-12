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
    
    # Add logs
    now = datetime.utcnow()
    l1 = DrugLog(user_id=user_id, drug_name="DrugA", dosage="10mg", datetime=now - timedelta(hours=2))
    l2 = DrugLog(user_id=user_id, drug_name="DrugB", dosage="20mg", datetime=now - timedelta(hours=10))
    l3 = DrugLog(user_id=user_id, drug_name="DrugC", dosage="30mg", datetime=now - timedelta(hours=5))
    l4 = DrugLog(user_id=user_id, drug_name="DrugD", dosage="40mg", datetime=now - timedelta(hours=48)) # old
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
    # Only seed once if using fixture, but we are using fresh db per function?
    # conftest clean_db runs autouse so it cleans up every function.
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
