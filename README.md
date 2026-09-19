
# Darukaa.Earth — AI Biodiversity Intelligence

A knowledge-grounded environmental decision-support prototype for the Darukaa.Earth hackathon.

## What it demonstrates
- RAG-style retrieval over a curated environmental knowledge base.
- Structured environmental schema + natural-language parsing.
- Clarifying questions when critical inputs are missing.
- Session memory endpoint for multi-turn environmental state.
- Multi-metric reasoning across soil, rainfall/climate, land use and human-impact indicators.
- Traceable recommendation output: action, mechanism, impacted metrics, horizon, confidence and evidence URLs.
- FastAPI backend + lightweight responsive web UI.
- No API key is required for the local prototype.

## Architecture
Browser → FastAPI API → Input Parser → Environmental State → TF-IDF Retrieval → Rule/Metric Reasoner → Output Validator/Contract → Response.

## Knowledge sources
The starter knowledge base contains FAO sources on soil biodiversity, soil organic carbon, agroforestry, cover crops and climate resilience. Each document stores title, organization, year, topic, source URL and retrievable text.

## Schema
EnvironmentalObservation: soil_ph, soil_organic_carbon, soil_moisture, temperature, rainfall, land_use, pollution_index, deforestation_index.
BiodiversityIndicator: species_richness, habitat_diversity.
Location: region, latitude, longitude, climate_zone.
EvidenceDocument: title, organization, year, topic, source_url, text, embedding_id.
ConversationSession: session key, messages/state, last_updated.

## Local setup
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000

## Demo
Use:
"Soil organic carbon: 0.3%. Rainfall: low. Crop: monoculture wheat. Region: semi-arid."

The UI should return an agroforestry/intercropping evaluation with impacted metrics and retrieved FAO evidence.

## API
POST `/api/analyze`
```json
{
  "message":"Soil organic carbon: 0.3%. Rainfall: low. Crop: monoculture wheat. Region: semi-arid."
}
```

POST `/api/session/{session_id}` preserves environmental state across turns.

GET `/api/health` and `/api/schema` are available for verification.

## Tests
Run:
```bash
pytest -q
```

## CI/CD
GitHub Actions runs a syntax/import smoke test on pushes and pull requests. For deployment, connect the repository to a Python-capable host such as Railway and set the start command:
`uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Secrets
Do not commit API keys, passwords, database credentials or private reviewer credentials. The current prototype intentionally uses no secret.

## Limitations
This is a hackathon prototype, not a field agronomy prescription engine. Real deployments should add geospatial datasets, calibrated thresholds, expert review, source versioning, stronger semantic embeddings/vector DB, user authentication and monitoring.
