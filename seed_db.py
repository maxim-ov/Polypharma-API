import os
import csv
import asyncio
import httpx
from database import engine, SessionLocal
from models.db_models import Base, Drug, DrugInteraction

# Ensure tables are created
Base.metadata.create_all(bind=engine)

async def get_rxcui_async(client, drug_name):
    """Fetch RxCUI for a drug name using RxNorm API."""
    url = "https://rxnav.nlm.nih.gov/REST/rxcui.json"
    params = {"name": drug_name, "search": 1}
    try:
        resp = await client.get(url, params=params)
        data = resp.json()
        rxnorm_id_list = data.get("idGroup", {}).get("rxnormId")
        if rxnorm_id_list:
            return rxnorm_id_list[0]
    except Exception as e:
        print(f"Error fetching RxCUI for {drug_name}: {e}")
    return None

async def fetch_all_rxcuis(drug_names):
    """Fetch RxCUIs for a list of drug names in parallel with rate limiting."""
    results = {}
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Process in batches to avoid overwhelming the API and respect rate limits
        batch_size = 20
        for i in range(0, len(drug_names), batch_size):
            batch = drug_names[i:i+batch_size]
            tasks = [get_rxcui_async(client, name) for name in batch]
            responses = await asyncio.gather(*tasks)
            for name, rxcui in zip(batch, responses):
                results[name] = rxcui
            print(f"Processed {min(i + batch_size, len(drug_names))}/{len(drug_names)} drugs...")
            # Small sleep to be nice to the API
            await asyncio.sleep(0.1)
    return results

def seed():
    db = SessionLocal()

    datasets_dir = "datasets"
    if not os.path.exists(datasets_dir):
        print(f"Directory {datasets_dir} not found. Are you missing datasets?")
        return
    
    drugs = {} # id -> name
    interactions = []
    
    csv_files = [f for f in os.listdir(datasets_dir) if f.endswith(".csv")]
    if not csv_files:
        print("No CSV files found in datasets/")
        return
        
    for filename in csv_files:
        category = filename.split("_")[-1].replace(".csv", "")
        filepath = os.path.join(datasets_dir, filename)
        
        print(f"Processing {filename}...")
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                id_a = row["DDInterID_A"].strip()
                name_a = row["Drug_A"].strip()
                id_b = row["DDInterID_B"].strip()
                name_b = row["Drug_B"].strip()
                level = row["Level"].strip()
                
                if id_a not in drugs:
                    drugs[id_a] = name_a
                if id_b not in drugs:
                    drugs[id_b] = name_b
                
                interactions.append({
                    "drug_a_id": id_a,
                    "drug_b_id": id_b,
                    "level": level,
                    "category": category
                })

    print(f"\nFound {len(drugs)} unique drugs.")
    
    # Fetch RxCUIs
    print("Fetching RxCUIs from RxNorm (this may take a few minutes)...")
    unique_names = list(set(drugs.values()))
    rxcui_map = asyncio.run(fetch_all_rxcuis(unique_names))

    print(f"Found {len(interactions)} interactions to insert.")

    print("Clearing database...")
    db.query(DrugInteraction).delete()
    db.query(Drug).delete()
    db.commit()

    print("Inserting drugs...")
    drug_mappings = [
        {"id": k, "name": v, "rxcui": rxcui_map.get(v)} 
        for k, v in drugs.items()
    ]
    chunk_size = 5000
    for i in range(0, len(drug_mappings), chunk_size):
        db.bulk_insert_mappings(Drug, drug_mappings[i:i+chunk_size])
    db.commit()

    print("Inserting interactions...")
    for i in range(0, len(interactions), chunk_size):
        db.bulk_insert_mappings(DrugInteraction, interactions[i:i+chunk_size])
    db.commit()

    print("\nDatabase seeded successfully with RxCUIs!")

if __name__ == "__main__":
    seed()
