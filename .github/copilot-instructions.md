# AI Podcast Tracker - Copilot Instructions

## Project Overview

**PodcastTracker** is a FastAPI-based service that automatically tracks Spanish AI podcasts, fetches RSS feeds hourly, stores episodes in SQLite, and provides a REST API with a modern web UI. The system combines backend automation with frontend user interaction.

## Architecture

### Core Components

1. **FastAPI Backend** (`src/podcast_tracker/api/routes.py`)
   - RESTful endpoints for podcasts and episodes
   - Dependency injection with `get_db_session` for database access
   - Pagination support (page, page_size parameters)
   - Returns Pydantic schemas (not ORM models directly)

2. **Database Layer** (`src/podcast_tracker/database/`)
   - SQLAlchemy ORM with two core models: `Podcast` and `Episode`
   - SQLite by default (configured via `settings.database_url`)
   - Relationship: `Podcast.episodes` (cascade delete)
   - Key fields: `Episode.listened` (boolean), `Episode.pub_date` (DateTime)

3. **Services** (`src/podcast_tracker/services/`)
   - `PodcastService`: Business logic for adding/refreshing podcasts
   - `RSSParser`: Parses feeds using `feedparser` library, extracts metadata and episodes
   - `PodcastScheduler`: APScheduler-based background job (checks every `check_interval_hours`, default 1 hour)

4. **Configuration** (`src/podcast_tracker/config.py`)
   - Uses Pydantic Settings with `.env` file support
   - Key vars: `database_url`, `check_interval_hours`, `log_level`, `host`, `port`

### Data Flow

```
[FastAPI Routes] → [PodcastService] → [RSSParser] + [Database Models]
[Scheduler Job] → [PodcastService] → [RSSParser] + [Database Models]
[Frontend] ↔ [API Routes] → [Database]
```

## Key Patterns

### API Response Format
- Use Pydantic schemas (`src/podcast_tracker/api/schemas.py`) for responses, NOT ORM models
- Pagination returns `EpisodeListResponse` with `episodes`, `total`, `page`, `page_size`, `total_pages`
- Filter unlistened episodes by default: `filter(Episode.listened == False)`

### Database Session Management
- Always use `get_db_session` dependency: `db: Session = Depends(get_db_session)`
- Never create raw connections; ORM handles transactions
- Lazy load relationships carefully (e.g., `_ = episode.podcast` to trigger load)

### RSS Parsing
- `RSSParser.parse_feed(url)` returns `Dict` with `title`, `description`, `artwork_url`, `episodes`
- Episodes extracted via `feedparser` entries; dates parsed with `dateutil.parser`
- Handle `feed.bozo` warnings for malformed RSS gracefully

### Error Handling
- Log errors with `logger.error()` before returning None or raising HTTPException
- Use HTTPException(status_code=404, detail="...") for missing resources
- Check for duplicate podcasts by `rss_url` before adding

## Development Workflows

### Running the Application
```bash
cd podcast-tracker
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cd src
python -m podcast_tracker.main
# Server at http://localhost:8000; Swagger at /docs
```

### Running Tests
```bash
# All tests with coverage (must reach 80%)
pytest

# Unit tests only
pytest tests/unit/ -m unit

# Integration tests
pytest tests/integration/ -m integration

# Coverage report
pytest --cov=src/podcast_tracker --cov-report=html
```

### Key Test Setup
- `conftest.py` provides `test_db` fixture (in-memory SQLite)
- `client` fixture overrides `get_db_session` dependency with test DB
- Always mark tests with `@pytest.mark.unit` or `@pytest.mark.integration`

## Important Files & Their Roles

| File | Purpose |
|------|---------|
| `src/podcast_tracker/main.py` | App initialization, lifespan context, seed data |
| `src/podcast_tracker/api/routes.py` | All API endpoints and response logic |
| `src/podcast_tracker/database/models.py` | SQLAlchemy Podcast & Episode models |
| `src/podcast_tracker/services/podcast_service.py` | Add/refresh podcasts, check new episodes |
| `src/podcast_tracker/services/rss_parser.py` | RSS parsing, episode extraction |
| `src/podcast_tracker/services/scheduler.py` | APScheduler background job setup |
| `tests/conftest.py` | Pytest fixtures for DB and API client |

## Common Tasks

### Adding a New Endpoint
1. Define Pydantic schema in `api/schemas.py`
2. Add route in `api/routes.py` with `@router.get()` or `@router.post()`
3. Use `db: Session = Depends(get_db_session)` for DB access
4. Return schema-validated response
5. Add test in `tests/integration/test_api.py`

### Modifying Models
1. Update SQLAlchemy class in `database/models.py`
2. Add migration or recreate DB (development only)
3. Update Pydantic schema in `api/schemas.py` to match
4. Update tests in `tests/unit/test_models.py`

### Changing Scheduler Behavior
1. Edit `services/scheduler.py` (trigger, job function)
2. Change `check_interval_hours` in `config.py` or `.env`
3. Test with `pytest tests/` (scheduler starts in app startup)

## Testing Strategy

- **Unit tests** (`tests/unit/`) test models, services, and parsing logic in isolation
- **Integration tests** (`tests/integration/`) test API endpoints with test DB
- **80%+ coverage required** (enforced by pytest.ini)
- Use `test_db` and `client` fixtures from `conftest.py`
- Mock external RSS feeds in tests; don't fetch live

## Notes for AI Agents

- **Env vars matter**: Check `.env` before assuming defaults (database_url, check_interval_hours)
- **Async awareness**: FastAPI app is async-compatible; background scheduler runs separately
- **Database lifecycle**: Transactions auto-commit; use `db.commit()` after adds/updates in services
- **Static files**: `static/` folder mounted in main.py; frontend at `/` (index.html fallback)
- **Logging**: All major actions logged at INFO/DEBUG; check logs for scheduler job execution
