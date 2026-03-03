from fastapi import FastAPI
from routers import auth_router, drug_log_router, interaction_router

app = FastAPI(
    title="Polypharma API",
    description="REST API for logging drugs and checking drug-drug interactions (powered by DDInter2 data).",
    version="0.1.0",
)

# ── Register routers ──────────────────
app.include_router(auth_router.router)
app.include_router(drug_log_router.router)
app.include_router(interaction_router.router)


@app.get("/", tags=["Root"])
async def root():
    """Health-check / welcome endpoint."""
    return {"message": "Welcome to the Polypharma API"}
