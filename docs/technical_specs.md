# Human Design API - Technical Specification Document

**Version:** 4.0.0  
**Last Updated:** May 20, 2026  
**Author:** Dogan Turkuler (dogan.turkuler@gmail.com)  
**License:** AGPL-3.0-or-later OR LicenseRef-DevAIble-Commercial

---

## Executive Summary

The **Human Design API** is a high-performance Python-based REST API service that calculates comprehensive Human Design System metrics from birth data. It serves as a complete backend engine for modern Human Design applications, providing:

- **Core Calculations:** Energy Type, Strategy, Authority, Profile, Incarnation Cross, Variables, Planetary Positions
- **Advanced Features:** Dream Rave analysis, Global Cycle calculations, transit forecasting
- **Relationship Analysis:** Composite charts, Penta (group dynamics), Maia Matrix relational analytics
- **Visualization:** High-fidelity BodyGraph chart generation (PNG, SVG, JPG)

The API solves the primary problem of integrating rigorous astrological calculations (using Swiss Ephemeris) with modern application needs—providing fast, accurate, and scalable Human Design analytics via a clean REST interface.

---

## Technology Stack

### Programming Languages
- **Python 3.12+** (Primary language)

### Frameworks & Core Libraries
| Component | Technology | Purpose |
|-----------|------------|---------|
| Web Framework | **FastAPI** (≥0.115.0) | High-performance async web framework |
| Server | **Uvicorn** (0.27.1) | ASGI server for FastAPI |
| Data Validation | **Pydantic** (≥2.7.0) | Request/response schema validation |
| Astrology Engine | **pyswisseph** (2.10.3.2) | Swiss Ephemeris for planetary calculations |
| Geocoding | **geopy** (2.4.1) | Location to coordinates resolution |
| Timezone Resolution | **timezonefinder** (≥8.2.0) | Coordinate to timezone mapping |
| Visualization | **matplotlib** + **svgpath2mpl** | BodyGraph chart rendering |
| Data Processing | **numpy** (2.1.2), **pandas** (2.2.3) | Array and DataFrame operations |

### Infrastructure & Deployment
- **Containerization:** Docker with multi-stage builds
- **Orchestration:** Docker Compose
- **Image:** `dturkuler/humandesign_api:latest`
- **Exposed Port:** 9021 (configured in docker-compose.yml)
- **Database:** SQLite (`hd_data.sqlite`) for local data storage

### Development Tools
- **Linting:** Ruff
- **Testing:** Pytest
- **Environment Management:** python-dotenv

---

## System Architecture

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLIENT APPLICATIONS                              │
│  (Mobile Apps, Web Dashboards, Research Tools, Third-Party APIs)       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS / HTTP
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI APPLICATION                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │  V1 Router  │  │  V2 Router  │  │Transit Router│  │ Composite Router│ │
│  │  (Legacy)   │  │ (Flagship)  │  │  (Forecast)  │  │ (Relationships) │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘ │
│                                    │                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                    AUTHENTICATION LAYER                              ││
│  │              Bearer Token (HD_API_TOKEN)                             ││
│  └─────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         BUSINESS LOGIC LAYER                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐ │
│  │   Features   │ │   Services   │ │   Schemas    │ │     Utils       │ │
│  │  (Core Calc) │ │(Chart, Comp) │ │  (Pydantic)  │ │(Astro, Dates)   │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐ │
│  │ Swiss Ephem  │ │  Geopy/Nomin │ │  Timezone    │ │  SQLite (Local) │ │
│  │  (pyswisseph)│ │  (Geocoding) │ │  Finder      │ │  (hd_data)      │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Request Ingestion:**
   - Client sends HTTP request (GET for V1, POST for V2) with birth data
   - `Authorization: Bearer <token>` header validated by `dependencies.py`

2. **Geolocation & Timezone Resolution:**
   - If `latitude`/`longitude` provided: skip geocoding
   - Otherwise: `geopy.Nominatim` resolves place name to coordinates
   - `timezonefinder` converts coordinates to IANA timezone string
   - `pytz` calculates UTC offset (including DST)

3. **Timestamp Preparation:**
   - Birth timestamp tuple: `(year, month, day, hour, minute, second, utc_offset)`

4. **Core Calculation:**
   - `features/core.py::calc_single_hd_features()` performs Swiss Ephemeris calculations
   - Returns planetary positions, gates, lines, colors, tones, bases
   - `features/mechanics.py` derives channels, centers, type, authority, definition

5. **Enrichment (V2 Only):**
   - `services/enrichment.py` adds semantic layer (gate names, line descriptions, fixations)
   - `services/dream_rave.py` calculates Dream Rave activations
   - `services/global_cycles.py` determines Global Cycle context

6. **Response Formatting:**
   - V1: Direct JSON serialization via `utils/serialization.py`
   - V2: Pydantic models (`schemas/v2/`) with optional field masking via `services/masking.py`

7. **Visualization (if /bodygraph endpoint):**
   - `services/chart_renderer.py` generates BodyGraph using matplotlib
   - SVG paths from `data/layout_data.json` rendered with center/gate activations

---

## Core Modules & Logic

### 1. Entry Point & Routing (`src/humandesign/`)

| File | Purpose | Key Components |
|------|---------|----------------|
| `api.py` | FastAPI application factory | `app = FastAPI()`, router inclusion, version resolution |
| `dependencies.py` | Authentication | Bearer token validation, `verify_token()` dependency |
| `hd_constants.py` | Constants & mappings | Chakra mappings, gate meanings, type details, profile DB |

### 2. API Routers (`src/humandesign/routers/`)

| Router | Endpoints | Description |
|--------|-----------|-------------|
| `general.py` | `GET /calculate`, `GET /bodygraph`, `GET /health` | Legacy V1 endpoints |
| `v2/general.py` | `POST /v2/calculate` | Flagship V2 with enrichment & masking |
| `transits.py` | `GET /transits/daily`, `GET /transits/solar_return` | Transit forecasting |
| `composite.py` | `POST /analyze/composite`, `POST /analyze/compmatrix`, `POST /analyze/penta`, `POST /analyze/maia-penta` | Relationship & group analysis |

### 3. Business Logic (`src/humandesign/features/`)

| File | Purpose | Key Functions |
|------|---------|---------------|
| `core.py` | Core HD calculations | `calc_single_hd_features()`, `get_utc_offset_from_tz()`, `date_to_gate_dict()` |
| `mechanics.py` | HD mechanics derivation | `get_channels_and_active_chakras()`, `get_typ()`, `get_auth()`, `get_definition()` |
| `attributes.py` | Derived attributes | `get_inc_cross()`, `get_profile()`, `get_variables()` |

### 4. Services (`src/humandesign/services/`)

| Service | Responsibility |
|---------|----------------|
| `chart_renderer.py` | BodyGraph SVG/PNG/JPG generation using matplotlib |
| `composite.py` | Relationship analysis logic (composite charts, Penta, Maia Matrix) |
| `geolocation.py` | Singleton-based geocoding and timezone resolution |
| `enrichment.py` | Semantic enrichment (gate names, line descriptions, psychological profiles) |
| `dream_rave.py` | Dream Rave (sleep design) calculations |
| `global_cycles.py` | Global Cycle (1656-year macro-cycle) determination |
| `masking.py` | Selective output masking for V2 (`include`/`exclude` fields) |
| `sqlite_repository.py` | Local SQLite data access layer |

### 5. Data Layer (`src/humandesign/data/`)

- `layout_data.json`: SVG paths and coordinates for BodyGraph rendering (centers, channels, gates)
- Static JSON files referenced by `hd_constants.py`

### 6. Utilities (`src/humandesign/utils/`)

| Utility | Function |
|---------|----------|
| `serialization.py` | JSON formatting for general, gates, channels output |
| `astrology.py` | Western zodiac sign calculation from longitude |
| `date_utils.py` | Age calculation, ISO date formatting |
| `version.py` | Version string management (from `pyproject.toml`) |
| `health_utils.py` | Swiss Ephemeris health checks |

---

## Data Schema & API Contracts

### V2 Request Schema (`schemas/v2/calculate.py`)

```python
class CalculateRequestV2(BaseModel):
    year: int                    # Birth year (e.g., 1990)
    month: int                   # Birth month (1-12)
    day: int                     # Birth day (1-31)
    hour: int                    # Birth hour (0-23)
    minute: int                  # Birth minute (0-59)
    second: int = 0              # Birth second (optional)
    place: str                   # "City, Country" (e.g., "New York, USA")
    gender: Optional[str] = "male"
    islive: Optional[bool] = True
    latitude: Optional[float] = None   # Bypass geocoding if provided
    longitude: Optional[float] = None  # Bypass geocoding if provided
    include: Optional[List[str]] = None  # Field whitelist (e.g., ["general", "gates.personality"])
    exclude: Optional[List[str]] = None  # Field blacklist
```

### V2 Response Schema (Key Sections)

```python
class CalculateResponseV2(BaseModel):
    general: GeneralSectionV2      # Energy type, authority, profile, strategy, etc.
    centers: CentersV2             # defined: List[str], undefined: List[str]
    channels: List[Dict]           # Active channels with meanings
    gates: GatesV2                 # personality: Dict[str, GateV2], design: Dict[str, GateV2]
    variables: VariablesV2         # Cognitive orientation (top_right, bottom_right, etc.)
    advanced: AdvancedSectionV2    # dream_rave, global_cycle
```

### Key Endpoints Summary

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/v2/calculate` | POST | Bearer | Full chart calculation with enrichment |
| `/calculate` | GET | Bearer | Legacy V1 calculation |
| `/bodygraph` | GET | Bearer | Generate chart image (fmt=png/svg/jpg) |
| `/transits/daily` | GET | Bearer | Daily transit weather |
| `/transits/solar_return` | GET | Bearer | Yearly theme analysis |
| `/analyze/composite` | POST | Bearer | Pairwise relationship analysis |
| `/analyze/penta` | POST | Bearer | Group dynamics (3-5 people) |
| `/analyze/maia-penta` | POST | Bearer | Composite + Penta hybrid analysis |
| `/health` | GET | Bearer | Service health check |

### Chakra/Center Mapping

```python
chakra_map = {
    "HD": "Head",
    "AA": "Ajna", 
    "TT": "Throat",
    "GC": "G_Center",
    "HT": "Heart",
    "SN": "Spleen",
    "SP": "Solar Plexus",
    "SL": "Sacral",
    "RT": "Root"
}
```

---

## Setup & Deployment

### Prerequisites
- Docker 20.10+ and Docker Compose
- Git (for cloning)
- Optional: Python 3.12+ (for local development)

### Local Development Setup

```bash
# 1. Clone repository
git clone https://github.com/your-repo/humandesign_api.git
cd humandesign_api

# 2. Create environment file
cp .env_example .env
# Edit .env and set: HD_API_TOKEN=your_secret_token_here

# 3. Run with Docker Compose
docker-compose up --build -d

# 4. Verify health
curl -H "Authorization: Bearer your_token" http://localhost:9021/health
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `HD_API_TOKEN` | Yes | Bearer token for API authentication |

### Production Deployment

1. **Docker Image:** Uses multi-stage Dockerfile (builder + runtime)
   - Builder stage: Installs build deps (gcc, g++) for pyswisseph
   - Runtime stage: Slim Python 3.12 image with pre-installed dependencies

2. **Docker Compose Configuration:**
   ```yaml
   services:
     humandesign-api:
       image: dturkuler/humandesign_api:latest
       container_name: humandesignapi
       ports:
         - "9021:9021"
       environment:
         - HD_API_TOKEN=${HD_API_TOKEN}
       restart: always
   ```

3. **Port:** Exposed on 9021 (configurable in docker-compose.yml)

### CI/CD Considerations

- **Testing:** Run `pytest` in container or local environment
- **Linting:** `ruff check src/` for code quality
- **Versioning:** Single source of truth in `pyproject.toml` (read by `utils/version.py`)
- **OpenAPI:** `openapi.yaml` auto-generated/synced with FastAPI

---

## Maintenance & Extensibility

### Developer Guide

#### Adding a New API Endpoint

1. **Router:** Add to appropriate router in `src/humandesign/routers/`
   ```python
   @router.post("/new-endpoint")
   def new_endpoint(request: NewSchema, authorized: bool = Depends(verify_token)):
       # Implementation
       return response
   ```

2. **Schema:** Define request/response models in `src/humandesign/schemas/`
   ```python
   class NewRequest(BaseModel):
       field: str
   ```

3. **Register:** Import and include router in `src/humandesign/api.py`
   ```python
   from .routers import new_module
   app.include_router(new_module.router)
   ```

4. **Test:** Add test in `tests/test_new_endpoint.py`

#### Adding a New Chart Visualization Feature

1. Modify `src/humandesign/services/chart_renderer.py`
2. Update drawing logic in `draw_chart()` function
3. Layout data (SVG paths) stored in `src/humandesign/data/layout_data.json`
4. Test locally with `test_local.py` before committing

#### Updating Core Calculation Logic

1. **Location:** `src/humandesign/features/core.py`
2. **Key Function:** `calc_single_hd_features(timestamp, ...)`
3. **Testing:** Run `tests/test_core_calculations.py` to verify accuracy
4. **Regression:** Check `tests/regression/` for snapshot comparisons

#### Adding New Enrichment Data

1. **Service:** `src/humandesign/services/enrichment.py`
2. **Constants:** Add mappings to `src/humandesign/hd_constants.py`
3. **Approach:** Follow existing pattern of semantic field injection

### Common Tasks

| Task | Command/Location |
|------|-----------------|
| Run tests | `pytest tests/` |
| Run specific test | `pytest tests/test_v2_core.py -v` |
| Lint code | `ruff check src/humandesign` |
| Local dev server | `uvicorn src.humandesign.api:app --reload --port 8000` |
| Build Docker image | `docker build -t humandesign_api .` |
| View logs | `docker logs humandesignapi` |
| Access container shell | `docker exec -it humandesignapi /bin/bash` |

### Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `RuntimeError: HD_API_TOKEN not set` | Missing env var | Create `.env` file with `HD_API_TOKEN` |
| `401 Unauthorized` | Invalid/missing token | Check `Authorization: Bearer <token>` header |
| `500 Geocoding failed` | Network/place name issue | Verify place name format or provide lat/long directly |
| `ImportError: No module named 'swisseph'` | Missing build deps | Ensure Docker builder stage installs gcc/g++ |
| Chart rendering artifacts | Matplotlib version mismatch | Pin matplotlib version in requirements.txt |

### Performance Optimization Tips

1. **Geocoding Bypass:** Always provide `latitude` and `longitude` in requests to avoid Nominatim API calls (100x speedup)
2. **Field Masking:** Use `include` parameter in V2 to request only needed fields
3. **Singleton Pattern:** TimezoneFinder loaded once in RAM (`in_memory=True`)

---

## TODO: Documentation Improvements

The following areas could benefit from additional documentation:

1. **Algorithm Documentation:**
   - Detailed explanation of Swiss Ephemeris calculation parameters in `features/core.py`
   - Gate-to-channel mapping algorithm in `features/mechanics.py`
   - Penta group dynamics calculation logic in `services/composite.py`

2. **Data Schema:**
   - Complete JSON schema for `layout_data.json` (BodyGraph geometry)
   - Database schema for `hd_data.sqlite` (if used for more than ephemeral storage)
   - Explanation of `hd_constants.py` database structures (TYPE_DETAILS_MAP, PROFILE_DB, etc.)

3. **API Versioning Strategy:**
   - Deprecation timeline for V1 endpoints
   - Migration guide from V1 to V2

4. **Testing Strategy:**
   - How to add regression tests using `tests/regression/snapshots/`
   - Expected tolerance ranges for astrological calculations
   - Mocking strategy for geocoding in tests

5. **Chart Rendering:**
   - Document the BodyGraph coordinate system (240x320 canvas)
   - How to customize center colors or gate positions
   - SVG path format expected by `svgpath2mpl`

6. **Licensing & Commercial:**
   - Tier feature matrix in code (which features are locked to which tier)
   - How to implement custom licensing checks

7. **Deployment:**
   - Kubernetes deployment examples
   - Environment-specific configuration (dev/staging/prod)
   - Monitoring and observability setup (health checks, metrics)

8. **Error Handling:**
   - Complete error code reference
   - Retry strategies for external services (geocoding)

---

## Changelog Reference

See `CHANGELOG.md` for detailed version history. Key recent additions:
- **v4.0.0:** V2 Flagship API with semantic enrichment, Dream Rave, Global Cycles
- **v3.x:** Penta Analysis 2.0, Maia Matrix v2, Maia-Penta Hybrid
- **v2.x:** Composite analysis, transit endpoints
- **v1.x:** Core calculation engine, BodyGraph visualization

---

*End of Technical Specification Document*
