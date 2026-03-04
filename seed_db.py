import os
import csv
from database import engine, SessionLocal
from models.db_models import Base, Drug, DrugInteraction

# Ensure tables are created
Base.metadata.create_all(bind=engine)

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
        # e.g. ddinter_downloads_code_A.csv -> A
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
                
                # Collect unique drugs
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
    print(f"Found {len(interactions)} interactions to insert.")

    print("Clearing database...")
    db.query(DrugInteraction).delete()
    db.query(Drug).delete()
    db.commit()

    print("Inserting drugs...")
    drug_mappings = [{"id": k, "name": v} for k, v in drugs.items()]
    chunk_size = 10000
    for i in range(0, len(drug_mappings), chunk_size):
        db.bulk_insert_mappings(Drug, drug_mappings[i:i+chunk_size])
    db.commit()

    print("Inserting interactions...")
    for i in range(0, len(interactions), chunk_size):
        db.bulk_insert_mappings(DrugInteraction, interactions[i:i+chunk_size])
    db.commit()

    print("\nDatabase seeded successfully!")

if __name__ == "__main__":
    seed()
