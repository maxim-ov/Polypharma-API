# Polypharma-API
A REST API which helps resolve the polypharmacy issue by checking drug-drug interactions

## Example Run Through

Here is an example `curl` script running through the flow of all endpoints in the API:

```bash
# 1. Sign up
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'

# 2. Login to get an access token
curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'

# Extract the token (e.g. using jq or copy/pasting it)
# TOKEN=$(curl -s ... | jq -r .access_token)
TOKEN="<your_access_token_here>"

# 3. Log a drug
curl -X POST http://127.0.0.1:8000/drug-logs/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"drug_name": "Aspirin", "dosage": "500mg", "datetime": "2023-11-01T10:00:00"}'

# 4. Get all drug logs
curl -X GET http://127.0.0.1:8000/drug-logs/ \
  -H "Authorization: Bearer $TOKEN"

# 5. Update a drug log (assuming the ID of the created log was 1)
curl -X PUT http://127.0.0.1:8000/drug-logs/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dosage": "1000mg"}'

# 6. Check drug interactions
curl -X GET http://127.0.0.1:8000/interactions/major \
  -H "Authorization: Bearer $TOKEN"

curl -X GET http://127.0.0.1:8000/interactions/moderate \
  -H "Authorization: Bearer $TOKEN"

curl -X GET http://127.0.0.1:8000/interactions/minor \
  -H "Authorization: Bearer $TOKEN"

curl -X GET http://127.0.0.1:8000/interactions/safe \
  -H "Authorization: Bearer $TOKEN"

# 7. Ask the LLM agent about your current active medications
curl -X POST http://127.0.0.1:8000/interactions/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Can I drink grapefruit juice with these medications?"}'

# 8. Delete a drug log
curl -X DELETE http://127.0.0.1:8000/drug-logs/1 \
  -H "Authorization: Bearer $TOKEN"
```
