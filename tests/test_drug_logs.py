from datetime import datetime

def test_create_drug_log(client, auth_header):
    payload = {
        "drug_name": "Aspirin",
        "dosage": "500mg",
        "datetime": datetime.utcnow().isoformat()
    }
    response = client.post(
        "/drug-logs/",
        json=payload,
        headers=auth_header
    )
    assert response.status_code == 201
    data = response.json()
    assert data["drug_name"] == "Aspirin"
    assert data["dosage"] == "500mg"
    assert "id" in data
    assert "user_id" in data

def test_create_drug_log_unauthenticated(client):
    response = client.post(
        "/drug-logs/",
        json={"drug_name": "Aspirin", "dosage": "500mg", "datetime": datetime.utcnow().isoformat()}
    )
    assert response.status_code == 401

def test_get_drug_logs(client, auth_header):
    # Empty initially
    resp1 = client.get("/drug-logs/", headers=auth_header)
    assert resp1.status_code == 200
    assert len(resp1.json()) == 0

    # Add a log
    client.post(
        "/drug-logs/",
        json={"drug_name": "Paracetamol", "dosage": "1000mg", "datetime": datetime.utcnow().isoformat()},
        headers=auth_header
    )

    # Should contain 1 log
    resp2 = client.get("/drug-logs/", headers=auth_header)
    assert resp2.status_code == 200
    assert len(resp2.json()) == 1
    assert resp2.json()[0]["drug_name"] == "Paracetamol"

def test_update_drug_log(client, auth_header):
    # Create
    create_resp = client.post(
        "/drug-logs/",
        json={"drug_name": "Ibuprofen", "dosage": "200mg", "datetime": datetime.utcnow().isoformat()},
        headers=auth_header
    )
    log_id = create_resp.json()["id"]

    # Update
    update_resp = client.put(
        f"/drug-logs/{log_id}",
        json={"dosage": "400mg"},
        headers=auth_header
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["dosage"] == "400mg"
    assert update_resp.json()["drug_name"] == "Ibuprofen"  # Unchanged field

def test_update_nonexistent_log(client, auth_header):
    response = client.put(
        "/drug-logs/9999",
        json={"dosage": "400mg"},
        headers=auth_header
    )
    assert response.status_code == 404

def test_delete_drug_log(client, auth_header):
    # Create
    create_resp = client.post(
        "/drug-logs/",
        json={"drug_name": "Cetirizine", "dosage": "10mg", "datetime": datetime.utcnow().isoformat()},
        headers=auth_header
    )
    log_id = create_resp.json()["id"]

    # Delete
    delete_resp = client.delete(f"/drug-logs/{log_id}", headers=auth_header)
    assert delete_resp.status_code == 200
    
    # Retrieve should be empty
    get_resp = client.get("/drug-logs/", headers=auth_header)
    assert len(get_resp.json()) == 0

def test_delete_nonexistent_log(client, auth_header):
    response = client.delete("/drug-logs/9999", headers=auth_header)
    assert response.status_code == 404
