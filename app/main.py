from pathlib import Path
import json
import re
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
KB_FILE = DATA_DIR / "knowledge_base.json"


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Darukaa.Earth Biodiversity Intelligence System",
    description="AI-powered Biodiversity Intelligence System",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# FRONTEND
# ============================================================

app.mount(
    "/frontend",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="frontend",
)


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


# ============================================================
# KNOWLEDGE BASE
# ============================================================

if KB_FILE.exists():
    with open(KB_FILE, "r", encoding="utf-8") as f:
        KNOWLEDGE_BASE = json.load(f)
else:
    KNOWLEDGE_BASE = []


documents = []

for item in KNOWLEDGE_BASE:
    text = " ".join(
        [
            str(item.get("title", "")),
            str(item.get("topic", "")),
            str(item.get("text", "")),
            str(item.get("abstract", "")),
        ]
    )
    documents.append(text)


if documents:
    VECTOR_INDEX = TfidfVectorizer(
        stop_words="english"
    )

    DOCUMENT_MATRIX = VECTOR_INDEX.fit_transform(documents)

else:
    VECTOR_INDEX = None
    DOCUMENT_MATRIX = None


# ============================================================
# SESSION MEMORY
# ============================================================

SESSIONS = {}


# ============================================================
# INPUT MODEL
# ============================================================

class EnvironmentInput(BaseModel):
    message: str

    soil_ph: Optional[float] = None
    soil_organic_carbon: Optional[float] = None
    soil_moisture: Optional[float] = None

    temperature: Optional[float] = None
    rainfall: Optional[float] = None
    humidity: Optional[float] = None

    land_use: Optional[str] = None

    pollution_index: Optional[float] = None
    deforestation_index: Optional[float] = None

    species_richness: Optional[float] = None
    habitat_diversity: Optional[float] = None

    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


# ============================================================
# MESSAGE PARSER
# ============================================================

def parse_message(message: str):

    data = {}

    text = message.lower()

    # --------------------------------------------------------
    # Soil organic carbon
    # --------------------------------------------------------

    match = re.search(
        r"(?:soil organic carbon|organic carbon|soc)"
        r"\s*(?:is|=|:)?\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
        text,
    )

    if match:
        data["soil_organic_carbon"] = float(match.group(1))

    # --------------------------------------------------------
    # Soil pH
    # --------------------------------------------------------

    match = re.search(
        r"(?:soil\s*)?ph\s*(?:is|=|:)?\s*([0-9]+(?:\.[0-9]+)?)",
        text,
    )

    if match:
        data["soil_ph"] = float(match.group(1))

    # --------------------------------------------------------
    # Soil moisture
    # --------------------------------------------------------

    match = re.search(
        r"(?:soil moisture|moisture)"
        r"\s*(?:is|=|:)?\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
        text,
    )

    if match:
        data["soil_moisture"] = float(match.group(1))

    # --------------------------------------------------------
    # Rainfall
    # --------------------------------------------------------

    match = re.search(
        r"rainfall\s*(?:is|=|:)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:mm)?",
        text,
    )

    if match:
        data["rainfall"] = float(match.group(1))

    else:
        if "low rainfall" in text:
            data["rainfall"] = 300.0

        elif "high rainfall" in text:
            data["rainfall"] = 1500.0

        elif "moderate rainfall" in text:
            data["rainfall"] = 800.0

    # --------------------------------------------------------
    # Temperature
    # --------------------------------------------------------

    match = re.search(
        r"(?:temperature|temp)"
        r"\s*(?:is|=|:)?\s*(-?[0-9]+(?:\.[0-9]+)?)\s*°?\s*c?",
        text,
    )

    if match:
        data["temperature"] = float(match.group(1))

    # --------------------------------------------------------
    # Humidity
    # --------------------------------------------------------

    match = re.search(
        r"humidity\s*(?:is|=|:)?\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
        text,
    )

    if match:
        data["humidity"] = float(match.group(1))

    # --------------------------------------------------------
    # Pollution
    # --------------------------------------------------------

    match = re.search(
        r"pollution\s*(?:index)?\s*(?:is|=|:)?\s*([0-9]+(?:\.[0-9]+)?)",
        text,
    )

    if match:
        data["pollution_index"] = float(match.group(1))

    elif "high pollution" in text:
        data["pollution_index"] = 0.8

    elif "moderate pollution" in text:
        data["pollution_index"] = 0.5

    elif "low pollution" in text:
        data["pollution_index"] = 0.2

    # --------------------------------------------------------
    # Deforestation
    # --------------------------------------------------------

    match = re.search(
        r"deforestation\s*(?:index)?\s*(?:is|=|:)?\s*([0-9]+(?:\.[0-9]+)?)",
        text,
    )

    if match:
        data["deforestation_index"] = float(match.group(1))

    elif "high deforestation" in text:
        data["deforestation_index"] = 0.8

    elif "moderate deforestation" in text:
        data["deforestation_index"] = 0.5

    elif "low deforestation" in text:
        data["deforestation_index"] = 0.2

    # --------------------------------------------------------
    # Species richness
    # --------------------------------------------------------

    match = re.search(
        r"species richness\s*(?:is|=|:)?\s*([0-9]+(?:\.[0-9]+)?)",
        text,
    )

    if match:
        data["species_richness"] = float(match.group(1))

    elif "low species richness" in text:
        data["species_richness"] = 0.2

    # --------------------------------------------------------
    # Habitat diversity
    # --------------------------------------------------------

    match = re.search(
        r"habitat diversity\s*(?:is|=|:)?\s*([0-9]+(?:\.[0-9]+)?)",
        text,
    )

    if match:
        data["habitat_diversity"] = float(match.group(1))

    elif "low habitat diversity" in text:
        data["habitat_diversity"] = 0.2

    # --------------------------------------------------------
    # Land use
    # --------------------------------------------------------

    land_use_options = [
        "monoculture",
        "cropland",
        "crop",
        "forest",
        "pasture",
        "urban",
        "wetland",
        "plantation",
        "grassland",
    ]

    for option in land_use_options:
        if option in text:
            data["land_use"] = option
            break

    # --------------------------------------------------------
    # Region
    # --------------------------------------------------------

    region_patterns = [
        r"region\s*(?:is|=|:)?\s*([a-zA-Z][a-zA-Z\s-]{2,40})",
        r"area\s*(?:is|=|:)?\s*([a-zA-Z][a-zA-Z\s-]{2,40})",
    ]

    for pattern in region_patterns:
        match = re.search(pattern, message, re.IGNORECASE)

        if match:
            data["region"] = match.group(1).strip()
            break

    return data


# ============================================================
# MERGE SESSION DATA
# ============================================================

def merge_inputs(
    existing: dict,
    new_data: dict
):

    merged = existing.copy()

    for key, value in new_data.items():

        if value is not None:
            merged[key] = value

    return merged


# ============================================================
# MISSING INFORMATION
# ============================================================

def missing_questions(data: dict):

    questions = []

    # Soil carbon
    if data.get("soil_organic_carbon") is None:
        questions.append(
            "What is the soil organic carbon (SOC) level?"
        )

    # Rainfall
    if data.get("rainfall") is None:
        questions.append(
            "What is the approximate annual rainfall?"
        )

    # Land use
    if not data.get("land_use"):
        questions.append(
            "What is the current land use or cropping pattern?"
        )

    # Soil moisture
    if data.get("soil_moisture") is None:
        questions.append(
            "Do you have a recent soil moisture measurement?"
        )

    # Biodiversity
    if data.get("species_richness") is None:
        questions.append(
            "Do you have an estimate of species richness or biodiversity decline?"
        )

    return questions


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve(query: str, top_k: int = 4):

    if (
        not documents
        or VECTOR_INDEX is None
        or DOCUMENT_MATRIX is None
    ):
        return []

    query_vector = VECTOR_INDEX.transform([query])

    scores = cosine_similarity(
        query_vector,
        DOCUMENT_MATRIX
    )[0]

    ranked_indices = scores.argsort()[::-1]

    results = []

    for index in ranked_indices[:top_k]:

        score = float(scores[index])

        if score <= 0:
            continue

        item = KNOWLEDGE_BASE[index].copy()

        item["retrieval_score"] = round(score, 3)

        results.append(item)

    return results


# ============================================================
# RECOMMENDATION ENGINE
# ============================================================

def recommend(data: dict):

    actions = []
    signals = []
    impacted_metrics = []

    # --------------------------------------------------------
    # LOW SOIL ORGANIC CARBON
    # --------------------------------------------------------

    soc = data.get("soil_organic_carbon")

    if soc is not None and soc < 1.0:

        actions.append(
            "Increase soil organic matter using compost, crop residues, cover crops, and reduced soil disturbance."
        )

        signals.append(
            f"Low soil organic carbon ({soc}%)"
        )

        impacted_metrics.extend(
            [
                "soil organic carbon",
                "soil structure",
                "water retention",
            ]
        )

    # --------------------------------------------------------
    # LOW RAINFALL
    # --------------------------------------------------------

    rainfall = data.get("rainfall")

    if rainfall is not None and rainfall < 500:

        actions.append(
            "Use water-conserving practices such as mulching, rainwater harvesting, drought-tolerant native vegetation, and reduced evaporation."
        )

        signals.append(
            f"Low rainfall ({rainfall} mm/year)"
        )

        impacted_metrics.extend(
            [
                "soil moisture",
                "water availability",
                "plant survival",
            ]
        )

    # --------------------------------------------------------
    # MONOCULTURE
    # --------------------------------------------------------

    land_use = str(
        data.get("land_use") or ""
    ).lower()

    if "monoculture" in land_use:

        actions.append(
            "Introduce crop diversity, native vegetation strips, cover crops, and habitat patches."
        )

        signals.append(
            "Monoculture land-use pattern"
        )

        impacted_metrics.extend(
            [
                "habitat diversity",
                "pollinator abundance",
                "species richness",
            ]
        )

    # --------------------------------------------------------
    # LOW SOIL MOISTURE
    # --------------------------------------------------------

    moisture = data.get("soil_moisture")

    if moisture is not None and moisture < 30:

        actions.append(
            "Increase ground cover and mulching to reduce evaporation and improve soil moisture retention."
        )

        signals.append(
            f"Low soil moisture ({moisture}%)"
        )

        impacted_metrics.append(
            "soil moisture"
        )

    # --------------------------------------------------------
    # HIGH POLLUTION
    # --------------------------------------------------------

    pollution = data.get("pollution_index")

    if pollution is not None and pollution > 0.6:

        actions.append(
            "Identify major pollution sources, establish buffer zones, and restore vegetation near affected habitats."
        )

        signals.append(
            f"High pollution index ({pollution})"
        )

        impacted_metrics.extend(
            [
                "water quality",
                "habitat quality",
                "species health",
            ]
        )

    # --------------------------------------------------------
    # HIGH DEFORESTATION
    # --------------------------------------------------------

    deforestation = data.get(
        "deforestation_index"
    )

    if (
        deforestation is not None
        and deforestation > 0.6
    ):

        actions.append(
            "Protect remaining native vegetation and restore fragmented habitat using native species."
        )

        signals.append(
            f"High deforestation index ({deforestation})"
        )

        impacted_metrics.extend(
            [
                "habitat connectivity",
                "species richness",
                "ecosystem resilience",
            ]
        )

    # --------------------------------------------------------
    # LOW SPECIES RICHNESS
    # --------------------------------------------------------

    richness = data.get(
        "species_richness"
    )

    if (
        richness is not None
        and richness < 0.3
    ):

        actions.append(
            "Create habitat diversity through native plantings, ecological corridors, and pollinator-friendly vegetation."
        )

        signals.append(
            f"Low species richness ({richness})"
        )

        impacted_metrics.extend(
            [
                "species richness",
                "pollinator diversity",
                "habitat diversity",
            ]
        )

    # --------------------------------------------------------
    # LOW HABITAT DIVERSITY
    # --------------------------------------------------------

    habitat = data.get(
        "habitat_diversity"
    )

    if (
        habitat is not None
        and habitat < 0.3
    ):

        actions.append(
            "Restore multiple habitat types such as native vegetation patches, grassland, wetland edges, and shelter zones."
        )

        signals.append(
            f"Low habitat diversity ({habitat})"
        )

        impacted_metrics.extend(
            [
                "habitat diversity",
                "species richness",
            ]
        )

    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    if not actions:

        actions.append(
            "Collect baseline soil, climate, land-use, and biodiversity observations before selecting an intervention."
        )

        signals.append(
            "Insufficient environmental stress signals"
        )

        impacted_metrics.extend(
            [
                "soil health",
                "climate suitability",
                "biodiversity",
            ]
        )

    # Remove duplicate metrics
    impacted_metrics = list(
        dict.fromkeys(impacted_metrics)
    )

    # --------------------------------------------------------
    # TIME HORIZON
    # --------------------------------------------------------

    if len(actions) >= 3:
        time_horizon = (
            "6–24 months for measurable ecological improvement, "
            "with longer-term biodiversity benefits."
        )

    else:
        time_horizon = (
            "3–12 months for initial measurable improvements."
        )

    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    signal_count = len(signals)

    if signal_count >= 4:
        confidence = "High"

    elif signal_count >= 2:
        confidence = "Medium"

    else:
        confidence = "Low"

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    recommendation = actions[0]

    if len(actions) > 1:

        recommendation = (
            "Prioritize an integrated intervention combining "
            + " ".join(actions[:3])
        )

    why = (
        "The recommendation is based on the environmental "
        "signals provided and considers interactions between "
        "soil health, climate conditions, land use, and "
        "biodiversity."
    )

    return {
        "recommendation": recommendation,
        "why_it_works": why,
        "impacted_metrics": impacted_metrics,
        "time_horizon": time_horizon,
        "confidence": confidence,
        "signals_used": signals,
        "actions": actions,
    }


# ============================================================
# ANALYZE ENDPOINT
# ============================================================

@app.post("/api/analyze")
def analyze(payload: EnvironmentInput):

    session_id = (
        payload.region
        or "default-session"
    )

    # Parse information from message
    parsed = parse_message(
        payload.message
    )

    # Explicit structured values override
    # values parsed from text
    explicit_data = payload.model_dump(
        exclude={"message"},
        exclude_none=True,
    )

    parsed.update(explicit_data)

    # Get previous session
    previous = SESSIONS.get(
        session_id,
        {}
    )

    # Merge old + new observations
    merged = merge_inputs(
        previous,
        parsed,
    )

    # Save session memory
    SESSIONS[session_id] = merged

    # Determine missing information
    missing = missing_questions(
        merged
    )

    # Retrieve evidence
    retrieval_query = (
        payload.message
        + " "
        + " ".join(
            str(v)
            for v in merged.values()
            if v is not None
        )
    )

    evidence = retrieve(
        retrieval_query,
        top_k=4,
    )

    # --------------------------------------------------------
    # Clarification mode
    # --------------------------------------------------------

    if missing:

        return {
            "status": "needs_clarification",

            "message": (
                "I need a few more environmental observations "
                "to make the recommendation more reliable."
            ),

            "session_id": session_id,

            "observations": merged,

            "missing": missing,

            "evidence": evidence,

            "input_completeness": round(
                (
                    len(
                        [
                            value
                            for value in merged.values()
                            if value is not None
                        ]
                    )
                    / 10
                ),
                2,
            ),
        }

    # --------------------------------------------------------
    # Recommendation mode
    # --------------------------------------------------------

    result = recommend(
        merged
    )

    result.update(
        {
            "status": "complete",

            "session_id": session_id,

            "observations": merged,

            "evidence": evidence,

            "input_completeness": 1.0,
        }
    )

    return result


# ============================================================
# SESSION ENDPOINT
# ============================================================

@app.get("/api/session/{session_id}")
def get_session(session_id: str):

    return {
        "session_id": session_id,
        "observations": SESSIONS.get(
            session_id,
            {}
        ),
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():

    return {
        "status": "ok",
        "knowledge_documents": len(
            KNOWLEDGE_BASE
        ),
        "sessions": len(
            SESSIONS
        ),
    }


# ============================================================
# SCHEMA ENDPOINT
# ============================================================

@app.get("/api/schema")
def schema():

    return {
        "environmental_variables": [
            "soil_ph",
            "soil_organic_carbon",
            "soil_moisture",
            "temperature",
            "rainfall",
            "humidity",
            "land_use",
            "pollution_index",
            "deforestation_index",
            "species_richness",
            "habitat_diversity",
            "region",
            "latitude",
            "longitude",
        ],

        "knowledge_base_fields": [
            "title",
            "source_organization",
            "year",
            "topic",
            "source_url",
            "text",
            "abstract",
            "embedding_id",
        ],
    }
